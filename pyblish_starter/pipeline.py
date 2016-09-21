import os
import re
import sys
import logging
import datetime

from pyblish import api

self = sys.modules[__name__]

self._registered_data = list()
self._registered_families = list()
self._registered_root = None
self._registered_loader = None
self._registered_creator = None

self._log = logging.getLogger()


def setup(root, loader, creator):
    """Setup the running Python session.

    Arguments:
        root (str): Absolute path to assets
        loader (func): Function responsible for loading assets,
            takes `name` as argument.
        creator (func): Function responsible for creating instances,
            takes `name`, `family` and `use_selection` as argument.

    """

    register_root(root)
    register_loader(loader)
    register_creator(creator)

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


def ls(root):
    """List available assets"""
    dirname = os.path.join(root, "public")
    self._log.debug("Listing %s" % dirname)
    return os.listdir(dirname)


def register_root(root):
    self._registered_root = root


def register_loader(loader):
    self._registered_loader = loader


def register_creator(creator):
    self._registered_creator = creator


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


def registered_root():
    return self._registered_root


def registered_loader():
    return self._registered_loader


def registered_creator():
    return self._registered_creator


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
