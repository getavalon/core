"""Wrapper around interactions with the database"""

import os
import sys
import errno
import shutil
import logging
import tempfile
import contextlib

from . import schema, Session
from .vendor import requests
from .api import AvalonMongoDB, session_data_from_environment

# Third-party dependencies
from bson.objectid import ObjectId, InvalidId

__all__ = [
    "ObjectId",
    "InvalidId",
    "install",
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

self = sys.modules[__name__]

self._is_installed = False
self._connection_object = AvalonMongoDB(Session)
self._mongo_client = None
self._database = None

self._sentry_client = None
self._sentry_logging_handler = None

log = logging.getLogger(__name__)
PY2 = sys.version_info[0] == 2


def install():
    """Establish a persistent connection to the database"""
    if self._is_installed:
        return

    logging.basicConfig()

    self._connection_object.Session.update(_from_environment())
    self._connection_object.install()

    self._mongo_client = self._connection_object.mongo_client
    self._database = self._connection_object.database

    _install_sentry()

    self._is_installed = True


def _install_sentry():
    if not Session.get("AVALON_SENTRY"):
        return

    try:
        from raven import Client
        from raven.handlers.logging import SentryHandler
        from raven.conf import setup_logging
    except ImportError:
        # Note: There was a Sentry address in this Session
        return log.warning("Sentry disabled, raven not installed")

    client = Client(Session["AVALON_SENTRY"])

    # Transmit log messages to Sentry
    handler = SentryHandler(client)
    handler.setLevel(logging.WARNING)

    setup_logging(handler)

    self._sentry_client = client
    self._sentry_logging_handler = handler
    log.info("Connected to Sentry @ %s" % Session["AVALON_SENTRY"])


def _from_environment():
    session = session_data_from_environment(context_keys=True)

    session["schema"] = "avalon-core:session-2.0"
    try:
        schema.validate(session)
    except schema.ValidationError as e:
        # TODO(marcus): Make this mandatory
        log.warning(e)

    return session


def uninstall():
    """Close any connection to the database"""
    try:
        self._connection_object.uninstall()
    except AttributeError:
        pass

    self._mongo_client = None
    self._database = None
    self._is_installed = False


def active_project():
    """Return the name of the active project"""
    return self._connection_object.active_project()


def activate_project(project):
    """Establish a connection to a given collection within the database"""
    print("io.activate_project is deprecated")


def projects():
    """List available projects

    Returns:
        list of project documents

    """
    return self._connection_object.projects()


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


def insert_one(item, *args, **kwargs):
    assert isinstance(item, dict), "item must be of type <dict>"
    schema.validate(item)
    return self._connection_object.insert_one(item, *args, **kwargs)


def insert_many(items, *args, **kwargs):
    # check if all items are valid
    assert isinstance(items, list), "`items` must be of type <list>"
    for item in items:
        assert isinstance(item, dict), "`item` must be of type <dict>"
        schema.validate(item)

    return self._connection_object.insert_many(items, *args, **kwargs)


def find(*args, **kwargs):
    return self._connection_object.find(*args, **kwargs)


def find_one(filter, *args, **kwargs):
    assert isinstance(filter, dict), "filter must be <dict>"

    return self._connection_object.find_one(filter, *args, **kwargs)


def save(*args, **kwargs):
    """Deprecated, please use `replace_one`"""
    return self._connection_object.save(*args, **kwargs)


def replace_one(filter, replacement, *args, **kwargs):
    return self._connection_object.replace_one(
        filter, replacement, *args, **kwargs
    )


def update_one(*args, **kwargs):
    return self._connection_object.update_one(*args, **kwargs)


def update_many(filter, update, *args, **kwargs):
    return self._connection_object.update_many(filter, update, *args, **kwargs)


def distinct(*args, **kwargs):
    return self._connection_object.distinct(*args, **kwargs)


def aggregate(*args, **kwargs):
    return self._connection_object.aggregate(*args, **kwargs)


def drop(*args, **kwargs):
    return self._connection_object.drop(*args, **kwargs)


def delete_many(*args, **kwargs):
    return self._connection_object.delete_many(*args, **kwargs)


def parenthood(document):
    assert document is not None, "This is a bug"

    parents = list()

    while document.get("parent") is not None:
        document = find_one({"_id": document["parent"]})

        if document is None:
            break

        if document.get("type") == "master_version":
            _document = self.find_one({"_id": document["version_id"]})
            document["data"] = _document["data"]

        parents.append(document)

    return parents


@contextlib.contextmanager
def tempdir():
    tempdir = tempfile.mkdtemp()
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir)


def download(src, dst):
    """Download `src` to `dst`

    Arguments:
        src (str): URL to source file
        dst (str): Absolute path to destination file

    Yields tuple (progress, error):
        progress (int): Between 0-100
        error (Exception): Any exception raised when first making connection

    """

    try:
        response = requests.get(
            src,
            stream=True,
            auth=requests.auth.HTTPBasicAuth(
                Session["AVALON_USERNAME"],
                Session["AVALON_PASSWORD"]
            )
        )
    except requests.ConnectionError as e:
        yield None, e
        return

    with tempdir() as dirname:
        tmp = os.path.join(dirname, os.path.basename(src))

        with open(tmp, "wb") as f:
            total_length = response.headers.get("content-length")

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                downloaded = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    f.write(data)

                    yield int(100.0 * downloaded / total_length), None

        try:
            os.makedirs(os.path.dirname(dst))
        except OSError as e:
            # An already existing destination directory is fine.
            if e.errno != errno.EEXIST:
                raise

        shutil.copy(tmp, dst)
