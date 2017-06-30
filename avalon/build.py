import os
import sys
import json
import shutil
import tempfile
import subprocess

from avalon import lib, _session

CREATE_NO_WINDOW = 0x08000000
IS_WIN32 = sys.platform == "win32"


def run(src, fname, session):
    tempdir = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(mode="w+",
                                     dir=tempdir,
                                     suffix=".py",
                                     delete=False) as f:
        module_name = f.name
        f.write(src)

    executable = lib.which(session["AVALON_APP"])

    kwargs = dict(
        args=[executable, "-u", module_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        env=session,
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

        if popen.returncode != 0:
            for number, line in enumerate(src.splitlines()):
                sys.stdout.write("%i: %s\n" % (number + 1, line))

            sys.stdout.write("".join(output))

            raise RuntimeError("%s raised an error" % module_name)


def mayapy(fname):
    return """\
from maya import cmds, standalone
print("Initializing Maya..")
standalone.initialize()

from avalon import api

fname = r"{fname}"

cmds.file(fname, open=True, force=True, ignoreVersion=True)
context = api.publish()

success = all(
    result["success"]
    for result in context.data["results"]
)

assert success, "Publishing failed"
""".format(fname=fname)


def dispatch(root, job):
    print(job["message"])

    app = job["session"]["app"]
    src = {
        "mayapy2015": mayapy,
        "mayapy2016": mayapy,
        "mayapy2017": mayapy,
    }[app]

    job["session"]["projects"] = root
    job["session"]["mongo"] = os.getenv(
        "AVALON_MONGO", "mongodb://localhost:27017")

    with _session.new(**job["session"]) as session:
        for fname in job.get("resources", list()):
            print(" processing '%s'.." % fname)
            fname = os.path.join(root, fname)
            run(src(fname), fname, session)


if __name__ == '__main__':
    import logging
    import argparse

    logging.getLogger().setLevel(logging.WARNING)

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--file", default=os.path.join(
        os.getcwd(), "build.json"))

    kwargs = parser.parse_args()

    with open(kwargs.file) as f:
        script = json.load(f)

    for job in script:
        app = job["session"]["app"]
        # TODO: Check availability of software

        for resource in job["resources"]:
            # TODO: Check existence of resources
            break

    for job in script:
        dispatch(kwargs.root, job)
