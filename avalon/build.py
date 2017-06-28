import os
import sys
import time
import json
import shutil
import getpass
import tempfile
import subprocess

# Third-party dependencies
import pymongo

from avalon import api, lib
from avalon.vendor import six

CREATE_NO_WINDOW = 0x08000000
IS_WIN32 = sys.platform == "win32"


class Session(dict):
    def __enter__(self):
        return self.install()

    def __exit__(self, *args):
        self.uninstall()

    def __new__(cls, **kwargs):
        for key, value in kwargs.items():
            if not isinstance(key, six.string_types):
                raise TypeError("key '%s' was not a string" % key)

            if not isinstance(value, six.string_types):
                raise TypeError("value '%s' was not a string" % value)

        return super(Session, cls).__new__(cls, **kwargs)

    def __init__(self, **kwargs):
        super(Session, self).__init__(**kwargs)

        projects = kwargs.get("projects") or os.environ["AVALON_PROJECTS"]
        project = kwargs.get("project") or os.environ["AVALON_PROJECT"]
        asset = kwargs.get("asset") or os.environ["AVALON_ASSET"]
        silo = kwargs.get("silo") or os.environ["AVALON_SILO"]
        task = kwargs.get("task") or os.environ["AVALON_TASK"]
        app = kwargs.get("app") or os.environ["AVALON_APP"]
        mongo = (
            kwargs.get("mongo") or
            os.getenv("AVALON_MONGO",
                      "mongodb://localhost:27017")
        )

        config = kwargs.get("config") or os.environ["AVALON_CONFIG"]

        self.connection = None

        self.update({
            "AVALON_PROJECTS": projects,
            "AVALON_PROJECT": project,
            "AVALON_SILO": silo,
            "AVALON_ASSET": asset,
            "AVALON_TASK": task,
            "AVALON_CONFIG": config,
            "AVALON_APP": app,
            "AVALON_MONGO": mongo,
            "AVALON_DB": "mindbender",
            "AVALON_WORKDIR": None,

            "AVALON_CORE": os.path.dirname(os.path.dirname(__file__)),
            "PYTHONPATH": os.environ.get("PYTHONPATH", "")
        })

    def install(self):
        self.connection = self._connect()

        config = self.find_one({"type": "project"})["config"]
        template = config["template"]["work"]

        self["AVALON_WORKDIR"] = template.format(
            root=self["AVALON_PROJECTS"],
            app=self["AVALON_APP"],
            user=getpass.getuser(),
            **{
                key[len("AVALON_"):].lower(): value
                for key, value in self.items()
                if key != "AVALON_APP"
            }
        )

        self.application = lib.get_application(name=self["AVALON_APP"],
                                               environment=self)

        return dict(os.environ, **self)

    def uninstall(self):
        try:
            self.connection.close()
        except AttributeError:
            pass

    def _connect(self):
        client = pymongo.MongoClient(
            self["AVALON_MONGO"],
            serverSelectionTimeoutMS=2000
        )

        for retry in range(3):
            try:
                t1 = time.time()
                client.server_info()

            except OSError:
                api.logger.error("Retrying..")
                time.sleep(1)

            else:
                break

        else:
            raise IOError("ERROR: Couldn't connect to %s in "
                          "less than %.3f ms" % (self["AVALON_MONGO"], 2000))

        api.logger.info("Connected to server, delay %.3f s" % (
            time.time() - t1))

        return client

    def find_one(self, filter, projection=None, sort=None):
        assert isinstance(filter, dict), "filter must be <dict>"
        database = self.connection[self["AVALON_DB"]]
        collection = database[self["AVALON_PROJECT"]]
        return collection.find_one(
            filter=filter,
            projection=projection,
            sort=sort
        )


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

from maya import cmds
from avalon import maya

fname = r"{fname}"

cmds.file(fname, open=True, force=True, ignoreVersion=True)
context = maya.publish()

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

    with Session(**job["session"]) as session:
        for fname in job.get("resources", list()):
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
        for app in job["session"]["app"]:
            # TODO: Check availability of software
            pass

    for job in script:
        dispatch(kwargs.root, job)
