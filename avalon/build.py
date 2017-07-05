"""Project Builder API

Usage:
    $ cd project
    $ python -m avalon.build

"""


import os
import sys
import json
import shutil
import tempfile
import subprocess

from avalon import lib, session

AVALON_DEBUG = bool(os.getenv("AVALON_DEBUG"))


def run(src, fname, session):
    tempdir = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(mode="w+",
                                     dir=tempdir,
                                     suffix=".py",
                                     delete=False) as f:
        module_name = f.name
        f.write(src.format(fname=fname))

    executable = lib.which(session["AVALON_APP"])

    kwargs = dict(
        args=[executable, "-u", module_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        env=session.environment,
    )

    try:
        popen = subprocess.Popen(**kwargs)

        # Blocks until finished
        output = list()
        for line in iter(popen.stdout.readline, ""):
            output.append(line)

    finally:
        popen.wait()  # Wait for return code
        shutil.rmtree(tempdir)

        if AVALON_DEBUG or popen.returncode != 0:
            for number, line in enumerate(src.splitlines()):
                sys.stdout.write("%i: %s\n" % (number + 1, line))

            sys.stdout.write("".join(output))

        if popen.returncode != 0:
            raise RuntimeError("%s raised an error" % module_name)


mayapy = r"""\
import os
import sys
from maya import cmds, standalone
from avalon import api

print("Initializing Maya..")
standalone.initialize()

fname = r"{fname}"

cmds.file(fname, open=True, force=True, ignoreVersion=True)

saved = cmds.file(rename=os.path.basename(fname))
print("Saving to %s.." % saved)
cmds.file(save=True)

context = api.publish()

success = all(
    result["success"]
    for result in context.data["results"]
)

if not success:
    sys.stderr.write("Publishing failed\n")
    sys.exit(1)
"""


def dispatch(root, job):
    print(job["message"])

    app = job["session"]["app"]
    src = {
        "mayapy2015": mayapy,
        "mayapy2016": mayapy,
        "mayapy2017": mayapy,
    }[app]

    job["session"]["projects"] = os.path.dirname(root)

    mongo = os.getenv("AVALON_MONGO")
    if mongo:
        job["session"]["mongo"] = mongo

    with session.new(**job["session"]) as sess:
        print(sess.format()) if AVALON_DEBUG else ""

        for fname in job.get("resources", list()):
            print(" processing '%s'.." % fname)
            fname = os.path.join(root, fname)
            session.create_workdir(sess)
            run(src, fname, sess)


def cli(args=None):
    import logging
    import argparse

    logging.getLogger().setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(args or sys.argv[1:])
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--file", default=os.path.join(
        os.getcwd(), "build.json"))

    kwargs = parser.parse_args()

    try:
        with open(kwargs.file) as f:
            script = json.load(f)
    except OSError:
        print("Error: No 'build.json' file found @ %s" % kwargs.file)
        sys.exit(1)

    missing_apps = set()
    missing_resources = set()
    for job in script:
        app = job["session"]["app"]
        # TODO: Check availability of software
        try:
            lib.which(app)
        except ValueError:
            missing_apps.add(app)

        for resource in job["resources"]:
            # TODO: Check existence of resources
            if not os.path.exists(resource):
                missing_resources.add(resource)

    if missing_apps:
        sys.stderr.write("ERROR: Some applications were not found.\n")
        sys.stderr.write("\n".join(
            "- %s" % app for app in missing_apps)
        )
        sys.stderr.write("\n")
        return 1

    if missing_resources:
        sys.stderr.write("ERROR: Some resources were not found.\n")
        sys.stderr.write("\n".join(
            "- %s" % resource for resource in missing_resources)
        )
        sys.stderr.write("\n")
        return 1

    try:
        for job in script:
            dispatch(kwargs.root, job)
    except RuntimeError:
        sys.stderr.write("Project did not exist, try running --save first.\n")
        return 1


if __name__ == '__main__':
    sys.exit(cli(sys.argv[1:]))
