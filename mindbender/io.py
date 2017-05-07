import os
import sys

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
    self.find_one = self._collection.find_one
    self.insert_many = self._collection.insert_many
    self.save = self._collection.save
    self.drop = self._collection.drop


def insert_one(item):
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
