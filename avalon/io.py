"""Wrapper around interactions with the database"""

import os
import sys
import time
import errno
import shutil
import logging
import tempfile
import functools
import contextlib

from . import schema, Session
from .vendor import requests

# Third-party dependencies
import pymongo
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
self._mongo_client = None
self._sentry_client = None
self._sentry_logging_handler = None
self._database = None
self._is_installed = False

log = logging.getLogger(__name__)


def install():
    """Establish a persistent connection to the database"""
    if self._is_installed:
        return

    logging.basicConfig()
    Session.update(_from_environment())

    timeout = int(Session["AVALON_TIMEOUT"])
    self._mongo_client = pymongo.MongoClient(
        Session["AVALON_MONGO"], serverSelectionTimeoutMS=timeout)

    for retry in range(3):
        try:
            t1 = time.time()
            self._mongo_client.server_info()

        except Exception:
            log.error("Retrying..")
            time.sleep(1)
            timeout *= 1.5

        else:
            break

    else:
        raise IOError(
            "ERROR: Couldn't connect to %s in "
            "less than %.3f ms" % (Session["AVALON_MONGO"], timeout))

    log.info("Connected to %s, delay %.3f s" % (
        Session["AVALON_MONGO"], time.time() - t1))

    _install_sentry()

    self._database = self._mongo_client[Session["AVALON_DB"]]
    self._is_installed = True


def _install_sentry():
    if "AVALON_SENTRY" not in Session:
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
    session = {
        item[0]: os.getenv(item[0], item[1])
        for item in (
            # Root directory of projects on disk
            ("AVALON_PROJECTS", None),

            # Name of current Project
            ("AVALON_PROJECT", None),

            # Name of current Asset
            ("AVALON_ASSET", None),

            # Name of current silo
            ("AVALON_SILO", None),

            # Name of current task
            ("AVALON_TASK", None),

            # Name of current app
            ("AVALON_APP", None),

            # Path to working directory
            ("AVALON_WORKDIR", None),

            # Optional path to scenes directory (see Work Files API)
            ("AVALON_SCENEDIR", None),

            # Name of current Config
            # TODO(marcus): Establish a suitable default config
            ("AVALON_CONFIG", "no_config"),

            # Name of Avalon in graphical user interfaces
            # Use this to customise the visual appearance of Avalon
            # to better integrate with your surrounding pipeline
            ("AVALON_LABEL", "Avalon"),

            # Used during any connections to the outside world
            ("AVALON_TIMEOUT", "1000"),

            # Address to Asset Database
            ("AVALON_MONGO", "mongodb://localhost:27017"),

            # Name of database used in MongoDB
            ("AVALON_DB", "avalon"),

            # Address to Sentry
            ("AVALON_SENTRY", None),

            # Address to Deadline Web Service
            # E.g. http://192.167.0.1:8082
            ("AVALON_DEADLINE", None),

            # Enable features not necessarily stable, at the user's own risk
            ("AVALON_EARLY_ADOPTER", None),

            # Address of central asset repository, contains
            # the following interface:
            #   /upload
            #   /download
            #   /manager (optional)
            ("AVALON_LOCATION", "http://127.0.0.1"),

            # Boolean of whether to upload published material
            # to central asset repository
            ("AVALON_UPLOAD", None),

            # Generic username and password
            ("AVALON_USERNAME", "avalon"),
            ("AVALON_PASSWORD", "secret"),

            # Unique identifier for instances in working files
            ("AVALON_INSTANCE_ID", "avalon.instance"),
            ("AVALON_CONTAINER_ID", "avalon.container"),

            # Enable debugging
            ("AVALON_DEBUG", None),

        ) if os.getenv(item[0], item[1]) is not None
    }

    session["schema"] = "avalon-core:session-1.0"
    try:
        schema.validate(session)
    except schema.ValidationError as e:
        # TODO(marcus): Make this mandatory
        log.warning(e)

    return session


def uninstall():
    """Close any connection to the database"""
    try:
        self._mongo_client.close()
    except AttributeError:
        pass

    self._mongo_client = None
    self._database = None
    self._is_installed = False


def requires_install(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not self._is_installed:
            raise IOError("'io.%s()' requires install()" % f.__name__)
        return f(*args, **kwargs)

    return decorated


def auto_reconnect(f):
    """Handling auto reconnect in 3 retry times"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        for retry in range(3):
            try:
                return f(*args, **kwargs)
            except pymongo.errors.AutoReconnect:
                log.error("Reconnecting..")
                time.sleep(0.1)
        else:
            raise

    return decorated


@requires_install
def active_project():
    """Return the name of the active project"""
    return Session["AVALON_PROJECT"]


def activate_project(project):
    """Establish a connection to a given collection within the database"""
    print("io.activate_project is deprecated")


@requires_install
def projects():
    """List available projects

    Returns:
        list of project documents

    """
    @auto_reconnect
    def find_project(project):
        return self._database[project].find_one({"type": "project"})

    @auto_reconnect
    def collections():
        return self._database.collection_names()
    collection_names = collections()

    for project in collection_names:
        if project in ("system.indexes",):
            continue

        # Each collection will have exactly one project document
        document = find_project(project)

        if document is not None:
            yield document


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


@auto_reconnect
def insert_one(item):
    assert isinstance(item, dict), "item must be of type <dict>"
    schema.validate(item)
    return self._database[Session["AVALON_PROJECT"]].insert_one(item)


@auto_reconnect
def insert_many(items, ordered=True):
    # check if all items are valid
    assert isinstance(items, list), "`items` must be of type <list>"
    for item in items:
        assert isinstance(item, dict), "`item` must be of type <dict>"
        schema.validate(item)

    return self._database[Session["AVALON_PROJECT"]].insert_many(
        items,
        ordered=ordered)


@auto_reconnect
def find(filter, projection=None, sort=None):
    return self._database[Session["AVALON_PROJECT"]].find(
        filter=filter,
        projection=projection,
        sort=sort
    )


@auto_reconnect
def find_one(filter, projection=None, sort=None):
    assert isinstance(filter, dict), "filter must be <dict>"

    return self._database[Session["AVALON_PROJECT"]].find_one(
        filter=filter,
        projection=projection,
        sort=sort
    )


@auto_reconnect
def save(*args, **kwargs):
    """Deprecated, please use `replace_one`"""
    return self._database[Session["AVALON_PROJECT"]].save(
        *args, **kwargs)


@auto_reconnect
def replace_one(filter, replacement):
    return self._database[Session["AVALON_PROJECT"]].replace_one(
        filter, replacement)


@auto_reconnect
def update_many(filter, update):
    return self._database[Session["AVALON_PROJECT"]].update_many(
        filter, update)


@auto_reconnect
def distinct(*args, **kwargs):
    return self._database[Session["AVALON_PROJECT"]].distinct(
        *args, **kwargs)


@auto_reconnect
def drop(*args, **kwargs):
    return self._database[Session["AVALON_PROJECT"]].drop(
        *args, **kwargs)


@auto_reconnect
def delete_many(*args, **kwargs):
    return self._database[Session["AVALON_PROJECT"]].delete_many(
        *args, **kwargs)


def parenthood(document):
    assert document is not None, "This is a bug"

    parents = list()

    while document.get("parent") is not None:
        document = find_one({"_id": document["parent"]})

        if document is None:
            break

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
