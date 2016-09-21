import os
import re
import sys
import types
import logging
import datetime

from pyblish import api

self = sys.modules[__name__]

self._registered_data = list()
self._registered_families = list()

self._log = logging.getLogger()

# Mock host interface
host = types.ModuleType("default")
host.ls = lambda: ["Asset1", "Asset2"]
host.loader = lambda asset, version, representation: None
host.creator = lambda name, family: "my_instance"

self._registered_host = host


def install(host):
    """Install `host` into the running Python session.

    Arguments:
        host (module): A Python module containing the Pyblish
            starter host-interface.

    """

    host.install()

    register_host(host)
    register_plugins()

    register_data(key="id", value="pyblish.starter.instance")
    register_data(key="label", value="{name}")
    register_data(key="family", value="{family}")

    register_family(
        name="starter.model",
        help="Polygonal geometry for animation"
    )

    register_family(
        name="starter.rig",
        help="Character rig"
    )

    register_family(
        name="starter.animation",
        help="Pointcache"
    )


def ls():
    """List available assets"""
    root = self.registered_host().root()
    dirname = os.path.join(root, "public")
    self._log.debug("Listing %s" % dirname)

    try:
        return os.listdir(dirname)
    except OSError:
        return list()


def abspath(asset, version=-1, representation=None):
    root = registered_host().root()

    dirname = os.path.join(
        root,
        "public",
        asset
    )

    try:
        versions = os.listdir(dirname)
    except OSError:
        raise OSError("\"%s\" not found." % asset)

    # Automatically deduce version
    if version == -1:
        version = find_latest_version(versions)

    dirname = os.path.join(
        dirname,
        "v%03d" % version
    )

    try:
        representations = dict()
        for fname in os.listdir(dirname):
            name, ext = os.path.splitext(fname)
            representations[ext] = fname

        if not representations:
            raise OSError

    except OSError:
        raise OSError("v%03d of \"%s\" not found." % (version, asset))

    # Automatically deduce representation
    if representation is None:
        fname = representations.values()[0]

    return os.path.join(
        dirname,
        fname
    )


def register_host(host):
    for member in ("root",
                   "loader",
                   "creator"):
        assert hasattr(host, member), "Missing %s" % member

    self._registered_host = host


def register_plugins():
    """Register accompanying plugins"""
    from . import plugins
    plugin_path = os.path.dirname(plugins.__file__)
    api.register_plugin_path(plugin_path)


def register_data(key, value, help=None):
    """Register new default attribute

    Arguments:
        key (str): Name of data
        value (object): Arbitrary value of data
        help (str, optional): Briefly describe

    """

    self._registered_data.append({
        "key": key,
        "value": value,
        "help": help or ""
    })


def register_family(name, data=None, help=None):
    """Register family and attributes for family

    Arguments:
        name (str): Name of family
        data (dict, optional): Additional data, see
            :func:`register_data` for docstring on members
        help (str, optional): Briefly describe this family

    """

    self._registered_families.append({
        "name": name,
        "data": data or [],
        "help": help or ""
    })


def registered_families():
    return list(self._registered_families)


def registered_data():
    return list(self._registered_data)


def registered_host():
    return self._registered_host


def time():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%SZ")


def format_private_dir(root, name):
    dirname = os.path.join(root, "private", time(), name)
    return dirname


def find_latest_version(versions):
    """Return latest version from list of versions

    If multiple numbers are found in a single version,
    the last one found is used. E.g. (6) from "v7_22_6"

    Arguments:
        versions (list): Version numbers as string

    Example:
        >>> find_next_version(["v001", "v002", "v003"])
        4
        >>> find_next_version(["1", "2", "3"])
        4
        >>> find_next_version(["v1", "v0002", "verision_3"])
        4
        >>> find_next_version(["v2", "5_version", "verision_8"])
        9
        >>> find_next_version(["v2", "v3_5", "_1_2_3", "7, 4"])
        6
        >>> find_next_version(["v010", "v011"])
        12

    """

    highest_version = 0
    for version in versions:
        matches = re.findall(r"\d+", version)

        if not matches:
            continue

        version = int(matches[-1])
        if version > highest_version:
            highest_version = version

    return highest_version


def find_next_version(versions):
    """Return next version from list of versions

    See docstring for :func:`find_latest_version`.

    Arguments:
        versions (list): Version numbers as string

    Returns:
        int: Next version number

    """

    return find_latest_version(versions) + 1
