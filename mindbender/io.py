import os
import sys
import time
import functools

from . import schema

# Third-party dependencies
import pymongo
from bson.objectid import ObjectId

self = sys.modules[__name__]
self._client = None
self._database = None
self._collection = None
self._uri = os.getenv("MINDBENDER_MONGO", "mongodb://localhost:27017")
self._is_installed = False
self._is_activated = False
self._timeout = int(os.getenv("MINDBENDER_TIMEOUT", 1000))


def install():
    if self._is_installed:
        return

    self._client = pymongo.MongoClient(
        self._uri, serverSelectionTimeoutMS=self._timeout)
    self._database = self._client["mindbender"]

    try:
        t1 = time.time()
        self._client.server_info()
    except Exception:
        raise IOError("ERROR: Couldn't connect to %s in "
                      "less than %.3f ms" % (self._uri, self._timeout))

    print("Connected to server, delay %.3f s" % (time.time() - t1))
    self._is_installed = True


def activate_project(project):
    try:
        # Support passing dictionary object
        project = project["name"]
    except TypeError:
        pass

    self._collection = self._database[project]
    self._is_activated = True


def uninstall():
    self._client.close()
    self._client = None
    self._database = None
    self._collection = None
    self._is_installed = False
    self._is_activated = False


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
        try:
            parent = find_one({
                "type": type_,
                "name": name,
                "parent": parent
            }, {"_id": 1})["_id"]
        except TypeError:
            return None

    return parent


@requires_activation
def insert_one(item):
    assert isinstance(item, dict), "item must be of type <dict>"
    schema.validate(item)
    return self._collection.insert_one(item)


@requires_activation
def find(*args, **kwargs):
    return self._collection.find(*args, **kwargs)


@requires_activation
def save(*args, **kwargs):
    return self._collection.save(*args, **kwargs)


@requires_activation
def distinct(*args, **kwargs):
    return self._collection.distinct(*args, **kwargs)


@requires_activation
def find_one(*args, **kwargs):
    return self._collection.find_one(*args, **kwargs)


@requires_activation
def drop(*args, **kwargs):
    return self._collection.drop(*args, **kwargs)


@requires_activation
def delete_many(*args, **kwargs):
    return self._collection.delete_many(*args, **kwargs)


@requires_activation
def parenthood(document):
    parents = list()

    while document.get("parent") is not None:
        document = find_one({"_id": document["parent"]})

        if document is None:
            break

        parents.append(document)

    return parents


__all__ = [
    "install",
    "uninstall",
    "ObjectId",
]
