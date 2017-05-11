import os
import sys

from . import schema

# Third-party dependencies
import pymongo
from bson.objectid import ObjectId

self = sys.modules[__name__]
self._client = None
self._collection = None
self._uri = os.getenv("MINDBENDER_MONGO", "mongodb://localhost:27017")


def install(collection="assets"):
    self._client = pymongo.MongoClient(self._uri, serverSelectionTimeoutMS=500)

    try:
        self._client.server_info()
    except Exception:
        raise IOError("ERROR: Couldn't connect to %s" % self._uri)

    self._collection = self._client["mindbender"][collection]

    # Shorthand
    self.find = self._collection.find
    self.save = self._collection.save
    self.distinct = self._collection.distinct
    self.find_one = self._collection.find_one
    self.drop = self._collection.drop
    self.delete_many = self._collection.delete_many


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
            parent = self.find_one({
                "type": type_,
                "name": name,
                "parent": parent
            }, {"_id": 1})["_id"]
        except TypeError:
            return None

    return parent


def insert_one(item):
    assert isinstance(item, dict), "item must be of type <dict>"
    schema.validate(item)
    return self._collection.insert_one(item)


def uninstall():
    self._client.close()


def parenthood(document):
    parents = list()

    while document.get("parent") is not None:
        document = self.find_one({"_id": document["parent"]})

        if document is None:
            break

        parents.append(document)

    return parents


__all__ = [
    "install",
    "uninstall",
    "ObjectId",
]
