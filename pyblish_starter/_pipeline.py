import os
import re
import sys
import datetime

from pyblish import api

self = sys.modules[__name__]
self._registered_data = list()
self._registered_families = list()

self._root = None
self._loader = None
self._creator = None


def setup(root, loader, creator):
    """Setup the running Python session.

    Arguments:
        root (str): Absolute path to assets
        loader (func): Function responsible for loading assets,
            takes `name` as argument.
        creator (func): Function responsible for creating instances,
            takes `name`, `family` and `use_selection` as argument.

    """

    self._root = root
    self._loader = loader
    self._creator = creator

    register_plugins()

    register_default(key="id", value="pyblish.starter.instance")
    register_default(key="label", value="{name}")
    register_default(key="family", value="{family}")

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
    return os.listdir(os.path.join(root, "public"))


def register_plugins():
    """Register accompanying plugins"""
    from . import plugins
    plugin_path = os.path.dirname(plugins.__file__)
    api.register_plugin_path(plugin_path)


def register_default(key, value, help=None):
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
            :func:`register_default` for docstring on members
        help (str, optional): Briefly describe this family

    """

    self._registered_families.append({
        "name": name,
        "data": data or {},
        "help": help or ""
    })


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
