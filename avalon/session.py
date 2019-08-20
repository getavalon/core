import os
import time
import errno
import logging
import shutil
import getpass

# Third-party dependencies
import pymongo

from avalon import lib
from avalon.vendor import six

log = logging.getLogger(__name__)


def new(**kwargs):
    for key, value in kwargs.items():
        if not isinstance(key, six.string_types):
            raise TypeError("key '%s' was not a string" % key)

        if not isinstance(value, six.string_types):
            raise TypeError("value '%s' was not a string" % value)

    return _Session(**kwargs)


class _Session(dict):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __init__(self,
                 projects,
                 project,
                 asset,
                 silo,
                 task,
                 app,
                 config,
                 db="avalon",
                 mongo="mongodb://localhost:27017",
                 label="Avalon"):

        self.update({
            "AVALON_PROJECTS": projects,
            "AVALON_PROJECT": project,
            "AVALON_SILO": silo,
            "AVALON_ASSET": asset,
            "AVALON_TASK": task,
            "AVALON_CONFIG": config,
            "AVALON_APP": app,
            "AVALON_MONGO": mongo,
            "AVALON_DB": db,
            "AVALON_LABEL": label,

            # NOTE(marcus): Based on AVALON_APP
            "AVALON_WORKDIR": None,
        })

        self.state = {
            "config": None,
            "connection": None,
            "application": None,
            "database": None,
            "is_installed": False,
        }

        self.install()

    def format(self):
        return "\n".join("%s: %s" % (key, value)
                         for key, value in self.items())

    @property
    def environment(self):
        environment = dict(os.environ, **self)

        # The application depends on the active environment,
        # the resulting environment then depends on the application.
        # TODO(marcus): See if there is any way of removing this
        # circular dependency.
        application = self.state["application"]
        environment.update(application.get("environment", {}))

        return environment

    def install(self):
        if self.state.get("is_installed"):
            return

        connection = self._connect()

        try:
            project = next(self.find({"type": "project"}))
        except StopIteration:
            raise RuntimeError("Project '%s' does not exist"
                               % self["AVALON_PROJECT"])

        config = project["config"]
        template = config["template"]["work"]

        # Application READS from environment..
        application = lib.get_application(name=self["AVALON_APP"])

        self["AVALON_WORKDIR"] = template.format(
            root=self["AVALON_PROJECTS"],
            app=application["application_dir"],
            user=getpass.getuser(),
            **{
                key[len("AVALON_"):].lower(): value
                for key, value in self.items()
                if key != "AVALON_APP"
            }
        )

        self.state.update({
            "config": config,
            "connection": connection,
            "application": application,
            "is_installed": True,
        })

    def uninstall(self):
        if not self.state.get("is_installed"):
            return

        try:
            self.state["connection"].close()
        except AttributeError:
            pass

        self.state.clear()

    def find(self, *args, **kwargs):
        return self.state["database"].find(*args, **kwargs)

    def find_one(self, *args, **kwargs):
        return self.state["database"].find_one(*args, **kwargs)

    def insert_one(self, *args, **kwargs):
        return self.state["database"].insert_one(*args, **kwargs)

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
                log.error("Retrying..")
                time.sleep(1)

            else:
                break

        else:
            raise IOError("ERROR: Couldn't connect to %s in "
                          "less than %.3f ms" % (self["AVALON_MONGO"], 2000))

        log.info("Connected to server, delay %.3f s" % (
            time.time() - t1))

        database = client[self["AVALON_DB"]]
        collection = database[self["AVALON_PROJECT"]]

        self.state["database"] = collection

        return client


def create_workdir(session):
    workdir = session["AVALON_WORKDIR"]
    _makedirs(workdir)

    application = session.state["application"]
    for appdir in application.get("default_dirs", []):
        _makedirs(os.path.join(workdir, appdir))

    for src, dst in application.get("copy", {}).items():
        _copy(src, os.path.join(workdir, dst))


def _copy(src, dst):
    try:
        shutil.copy(src, dst)
    except OSError as e:
        if e.errno == errno.EEXIST:
            # An already existing working directory is fine.
            pass
        else:
            raise


def _makedirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            # An already existing working directory is fine.
            pass
        else:
            raise
