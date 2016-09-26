import os
import sys
import json
import types
import shutil
import logging
import tempfile
import contextlib

from pyblish import api

from . import lib, schema

self = sys.modules[__name__]

self.log = logging.getLogger("pyblish-starter")

self._registered_data = list()
self._registered_families = list()
self._registered_formats = list()
self._registered_root = os.getcwd()  # Default to current working directory
self._is_installed = False


def default_host():
    """A default host, in place of anything better

    This may be considered as reference for the
    interface a host must implement. It also ensures
    that the system runs, even when nothing is there
    to support it.

    """

    host = types.ModuleType("default")
    host.__dict__.update({
        "ls": lambda: [],
        "load": lambda asset, version, representation: None,
        "create": lambda name, family: "my_instance",
    })

    return host


def debug_host():
    host = types.ModuleType("standalone")
    host.__dict__.update({
        "ls": lambda: [],
        "load": lambda asset, version=-1, representation=None:
            sys.stdout.write(json.dumps({
                "asset": asset,
                "version": version,
                "representation": representation
            }, indent=4) + "\n"),
        "create": lambda name, family:
            sys.stdout.write(json.dumps({
                "name": name,
                "family": family,
            }, indent=4))
    })

    return host


self._registered_host = default_host()


def install(host):
    """Install `host` into the running Python session.

    Arguments:
        host (module): A Python module containing the Pyblish
            starter host-interface.

    """

    # Optional host install function
    if hasattr(host, "install"):
        host.install()

    register_host(host)
    register_plugins()
    register_default_data()
    register_default_families()

    self._is_installed = True
    self.log.info("Successfully installed Pyblish Starter!")


def uninstall():
    try:
        registered_host().uninstall()
    except AttributeError:
        pass

    deregister_host()
    deregister_plugins()
    deregister_default_data()
    deregister_default_families()

    self.log.info("Successfully uninstalled Pyblish Starter!")


def is_installed():
    """Return state of installation

    Returns:
        True if installed, False otherwise

    """

    return self._is_installed


def register_default_data():
    register_data(key="id", value="pyblish.starter.instance")
    register_data(key="name", value="{name}")
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


def ls(root=None):
    """List available assets

    Return a list of available assets.

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
        due to dependence on os.listdir()

    ..note: The order of versions returned is guaranteed to be sorted, so
        as to simplify retrieving the latest one via `versions[-1]`

    """

    assetsdir = lib.format_shared_dir(root or self._registered_root)

    for asset in lib.listdir(assetsdir):
        versionsdir = os.path.join(assetsdir, asset)

        asset_entry = {
            "schema": "pyblish-starter:asset-1.0",
            "name": asset,
            "versions": list()
        }

        for version in lib.listdir(versionsdir):
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

            asset_entry["versions"].append(data)

        # Sort versions by integer
        asset_entry["versions"].sort(key=lambda v: v["version"])

        schema.validate(asset_entry, "asset")

        yield asset_entry


@contextlib.contextmanager
def fixture(assets=["Asset1"], versions=1):
    """Build transient fixture of `assets` and `versions`

    Generate a temporary fixture of customisable assets
    with current metadata schema. This function is intended
    for use in tests and tutorials.

    Arguments:
        assets (list, optional): Names of assets to create,
            defaults to one asset named "Asset1"
        version (int, optional): Number of versions of each asset,
            defaults to 1 version.

    Thread Safety:
        This function modifies globals state and is
        therefore not thread-safe.

    Usage:
        >>> with fixture(assets=["MyAsset1"], versions=1):
        ...    for asset in ls():
        ...       assert asset["name"] == "MyAsset1"
        ...

    """

    tempdir = tempfile.mkdtemp()
    shared = os.path.join(
        tempdir,
        "shared"
    )

    os.makedirs(shared)

    for asset in assets:
        assetdir = os.path.join(shared, asset)
        os.makedirs(assetdir)

        for version in range(versions):
            version = lib.format_version(version + 1)
            versiondir = os.path.join(assetdir, version)
            os.makedirs(versiondir)

            fname = os.path.join(versiondir, asset + ".ma")
            open(fname, "w").close()  # touch

            fname = os.path.join(versiondir, ".metadata.json")

            with open(fname, "w") as f:
                json.dump({
                    "schema": "pyblish-starter:version-1.0",
                    "version": lib.parse_version(version),
                    "path": versiondir,
                    "time": "",
                    "author": "mottosso",
                    "source": os.path.join(
                        "{project}",
                        "maya",
                        "scenes",
                        "scene.ma"
                    ),
                    "representations": [
                        {
                            "schema": "pyblish-starter:representation-1.0",
                            "format": ".ma",
                            "path": os.path.join(
                                "{dirname}",
                                "%s{format}" % asset
                            ),
                        },
                    ]
                }, f)

    # Keep track of original root
    _ = self._registered_root

    try:
        self._registered_root = tempdir
        yield tempdir
    finally:
        self._registered_root = _
        shutil.rmtree(tempdir)


def register_root(path):
    """Register currently active root"""
    self._registered_root = path


def registered_root():
    """Return currently registered root"""
    return self._registered_root


# Alias
root = registered_root


def register_format(format):
    """Register a supported format

    A supported format is used to determine which of any available
    representations are relevant to the currently registered host.

    """

    self._registered_formats.append(format)


def register_host(host):
    missing = list()
    for member in ("load",
                   "create",
                   "ls",):
        if not hasattr(host, member):
            missing.append(member)

    assert not missing, (
        "Incomplete interface for host: '%s'\n"
        "Missing: %s" % (host, ", ".join(missing))
    )

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
