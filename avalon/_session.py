import os
import sys
import time
import getpass

# Third-party dependencies
import pymongo

from avalon import api, lib
from avalon.vendor import six

self = sys.modules[__name__]
self.current = None


def new(**kwargs):
    for key, value in kwargs.items():
        if not isinstance(key, six.string_types):
            raise TypeError("key '%s' was not a string" % key)

        if not isinstance(value, six.string_types):
            raise TypeError("value '%s' was not a string" % value)

    return _Session(**kwargs)


class _Session(dict):
    def __enter__(self):
        return self.install()

    def __exit__(self, *args):
        self.uninstall()

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
            "AVALON_DB": db,
            "AVALON_LABEL": label,

            "AVALON_WORKDIR": None,
        })

    @property
    def is_connected(self):
        return self.connection is not None

    def install(self):
        if self.is_connected:
            return

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

        environment = dict(os.environ, **self)

        # Application READS from environment..
        app = lib.get_application(
            name=self["AVALON_APP"],
            environment=environment
        )

        # And later WRITE to it..
        environment.update(app.get("environment", {}))

        # TODO(marcus): See if there is any way
        # of removing that circular dependency.

        return environment

    def uninstall(self):
        try:
            self.connection.close()
        except AttributeError:
            pass

        self.connection = None

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

        # Backwards compatibility with Avalon before it was Avalon
        if client["mindbender"].collection_names():
            self["AVALON_DB"] = "mindbender"

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
