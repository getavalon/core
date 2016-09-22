import os
import sys
import json
import types
import logging

from pyblish import api

from . import lib

self = sys.modules[__name__]

self.log = logging.getLogger()

self._registered_data = list()
self._registered_families = list()
self._registered_formats = list()


def default_host():
    """A default host, in place of anything better

    This may be considered as reference for the
    interface a host must implement. It also ensures
    that the system runs, even when nothing is there
    to support it.

    """

    host = types.ModuleType("default")
    host.__dict__.update({
        "ls": lambda: ["Asset1", "Asset2"],
        "loader": lambda asset, version, representation: None,
        "creator": lambda name, family: "my_instance",
        "supported_formats": lambda: [".ma", ".mb"]
    })

    return host

self._registered_host = default_host()


def install(host):
    """Install `host` into the running Python session.

    Arguments:
        host (module): A Python module containing the Pyblish
            starter host-interface.

    """

    try:
        # Optional host install function
        host.install()
    except AttributeError:
        pass

    register_host(host)
    register_plugins()
    register_default_data()
    register_default_families()


def uninstall():
    try:
        registered_host().uninstall()
    except AttributeError:
        pass

    deregister_host()
    deregister_plugins()
    deregister_default_data()
    deregister_default_families()


def ls():
    """List available assets

    Return a list of available assets.

    Schema:
        {
          "schema": "pyblish-starter:asset-1.0",
          "name": Name of directory,
          "versions": [
            {
              "version": 1,
              "comment": "",
              "representations": [
                {
                  "format": File extension,
                  "path": Filename
                }
              ]
            },
          ]
        }

    The interface of this function, along with its schema, is designed
    to facilitate a potential transition into database-driven queries.

    A note on performance:
        This function is a generator, it scans the system one asset
        at a time. However, scanning implies both listing directories
        and opening files - one per asset per version.

        Therefore, performance drops combinatorially for each new
        version added to the project.

        In small pipelines - e.g. 100s of assets, with 10s of versions -
        this should not pose a problem.

        In large pipelines - e.g. 1000s of assets, with 100s of versions -
        this would likely become unbearable and manifest itself in
        surrounding areas of the pipeline where disk-access is
        critical; such as saving or loading files.

    ..note: The order of the list is undefined, but is typically alphabetical
        due to how os.listdir() is implemented.

    ..note: The order of versions returned is guaranteed to be sorted, so
        as to simplify retrieving the latest one via `versions[-1]`

    """

    root = registered_host().root()
    assetsdir = os.path.join(root, "public")

    for asset in os.listdir(assetsdir):
        versionsdir = os.path.join(assetsdir, asset)

        asset_entry = {
            "schema": "pyblish-starter:asset-1.0",
            "name": asset,
            "versions": list()
        }

        for version in os.listdir(versionsdir):
            versiondir = os.path.join(versionsdir, version)
            fname = os.path.join(versiondir, ".metadata.json")

            try:
                with open(fname) as f:
                    data = json.load(f)

            except IOError:
                self.log.warning("\"%s\" not found." % fname)
                continue

            if data.get("schema") != "pyblish-starter:version-1.0":
                self.log.warning("\"%s\" unsupported schema." % fname)
                continue

            version_entry = {
                "version": lib.parse_version(version),
                "path": versiondir,
                "representations": list()
            }

            for representation in os.listdir(versiondir):
                if representation.startswith("."):
                    continue

                name, ext = os.path.splitext(representation)
                version_entry["representations"].append({
                    "format": ext,
                    "path": "{dirname}/%s{format}" % name
                })

            asset_entry["versions"].append(version_entry)

        # Sort versions by integer
        asset_entry["versions"].sort(key=lambda v: v["version"])

        yield asset_entry


def register_default_data():
    register_data(key="id", value="pyblish.starter.instance")
    register_data(key="label", value="{name}")
    register_data(key="family", value="{family}")


def register_default_families():
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


def register_host(host):
    for member in ("root",
                   "loader",
                   "creator",):
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


def registered_formats():
    return self._registered_formats[:]


def registered_families():
    return self._registered_families[:]


def registered_data():
    return self._registered_data[:]


def registered_host():
    return self._registered_host


def deregister_default_families():
    self._registered_families[:] = list()


def deregister_default_data():
    self._registered_data[:] = list()


def deregister_plugins():
    from . import plugins
    plugin_path = os.path.dirname(plugins.__file__)

    try:
        api.deregister_plugin_path(plugin_path)
    except ValueError:
        self.log.warning("pyblish-starter plug-ins not registered.")


def deregister_host():
    self._registered_host = default_host()
