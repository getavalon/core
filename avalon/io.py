"""Wrapper around interactions with the database"""

import os
import sys
import time
import functools

from . import schema, lib

# Third-party dependencies
import pymongo
from bson.objectid import ObjectId, InvalidId

__all__ = [
    "ObjectId",
    "InvalidId",
    "install",
    "active_project",
    "activate_project",
    "uninstall",
    "projects",
    "locate",
    "insert_one",
    "find",
    "find_one",
    "save",
    "replace_one",
    "update_many",
    "distinct",
    "drop",
    "delete_many",
    "parenthood",
]

AVALON_DB = os.getenv("AVALON_DB", "avalon")
AVALON_TIMEOUT = int(os.getenv("AVALON_TIMEOUT", "1000"))
AVALON_MONGO = os.getenv("AVALON_MONGO", "mongodb://localhost:27017")

self = sys.modules[__name__]
self._client = None
self._database = None
self._collection = None
self._is_installed = False
self._is_activated = False
self._timeout = AVALON_TIMEOUT


def install():
    """Establish a persistent connection to the database"""
    if self._is_installed:
        return

    self._client = pymongo.MongoClient(
        AVALON_MONGO, serverSelectionTimeoutMS=self._timeout)

    for retry in range(3):
        try:
            t1 = time.time()
            self._client.server_info()

        except Exception:
            lib.logger.error("Retrying..")
            time.sleep(1)
            self._timeout *= 1.5

        else:
            break

    else:
        raise IOError("ERROR: Couldn't connect to %s in "
                      "less than %.3f ms" % (AVALON_MONGO, self._timeout))

    lib.logger.info("Connected to server, delay %.3f s" % (time.time() - t1))
    self._database = self._client[AVALON_DB]
    self._is_installed = True


def uninstall():
    """Close any connection to the database"""
    try:
        self._client.close()
    except AttributeError:
        pass

    self._client = None
    self._database = None
    self._collection = None
    self._is_installed = False
    self._is_activated = False


def active_project():
    """Return the name of the active project"""
    return self._collection.name


def activate_project(project):
    """Establish a connection to a given collection within the database"""
    try:
        # Support passing dictionary object
        project = project["name"]
    except TypeError:
        pass

    self._collection = self._database[project]
    self._is_activated = True


def requires_install(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not self._is_installed:
            raise IOError("'io.%s()' requires install()" % f.__name__)
        return f(*args, **kwargs)

    return decorated


def requires_activation(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not self._is_activated:
            raise IOError("'io.%s()' requires an active project" % f.__name__)
        return f(*args, **kwargs)

    return decorated


@requires_install
def projects():
    """List available projects

    Returns:
        list of project documents

    """

    for project in self._database.collection_names():
        if project in ("system.indexes",):
            continue

        # Each collection will have exactly one project document
        document = self._database[project].find_one({
            "type": "project"
        })

        if document is not None:
            yield document


@requires_activation
def locate(path):
    """Traverse a hierarchy from top-to-bottom

    Example:
        representation = locate(["hulk", "Bruce", "modelDefault", 1, "ma"])

    Returns:
        representation (ObjectId)

    """

    components = zip(
        ("project", "asset", "subset", "version", "representation"),
        path
    )

    parent = None
    for type_, name in components:
        latest = (type_ == "version") and name in (None, -1)

        try:
            if latest:
                parent = find_one(
                    filter={
                        "type": type_,
                        "parent": parent
                    },
                    projection={"_id": 1},
                    sort=[("name", -1)]
                )["_id"]
            else:
                parent = find_one(
                    filter={
                        "type": type_,
                        "name": name,
                        "parent": parent
                    },
                    projection={"_id": 1},
                )["_id"]

        except TypeError:
            return None

    return parent


@requires_activation
def insert_one(item):
    assert isinstance(item, dict), "item must be of type <dict>"
    schema.validate(item)
    return self._collection.insert_one(item)


@requires_activation
def find(filter, projection=None, sort=None):
    return self._collection.find(
        filter=filter,
        projection=projection,
        sort=sort
    )


@requires_activation
def find_one(filter, projection=None, sort=None):
    assert isinstance(filter, dict), "filter must be <dict>"

    return self._collection.find_one(
        filter=filter,
        projection=projection,
        sort=sort
    )


@requires_activation
def save(*args, **kwargs):
    return self._collection.save(*args, **kwargs)


@requires_activation
def replace_one(filter, replacement):
    return self._collection.replace_one(filter, replacement)


@requires_activation
def update_many(filter, update):
    return self._collection.update_many(filter, update)


@requires_activation
def distinct(*args, **kwargs):
    return self._collection.distinct(*args, **kwargs)


@requires_activation
def drop(*args, **kwargs):
    return self._collection.drop(*args, **kwargs)


@requires_activation
def delete_many(*args, **kwargs):
    return self._collection.delete_many(*args, **kwargs)


@requires_activation
def parenthood(document):
    assert document is not None, "This is a bug"

    parents = list()

    while document.get("parent") is not None:
        document = find_one({"_id": document["parent"]})

        if document is None:
            break

        parents.append(document)

    return parents
