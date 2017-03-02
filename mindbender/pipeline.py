import os
import sys
import json
import types
import shutil
import logging
import inspect
import tempfile
import contextlib

from pyblish import api

from . import lib, schema
from . import (
    _registered_families,
    _registered_data,
    _registered_silos,
    _registered_formats,
    _registered_loader_paths,
    _registered_host,
    _registered_root,
)

from .vendor import six

self = sys.modules[__name__]

self.log = logging.getLogger("mindbender-core")
self._is_installed = False


def install(host):
    """Install `host` into the running Python session.

    Arguments:
        host (module): A Python module containing the Pyblish
            mindbender host-interface.

    """

    # Optional host install function
    if hasattr(host, "install"):
        host.install()

    register_host(host)
    register_plugins()

    self._is_installed = True
    self.log.info("Successfully installed Pyblish Mindbender!")


def uninstall():
    try:
        registered_host().uninstall()
    except AttributeError:
        pass

    deregister_host()
    deregister_plugins()

    self.log.info("Successfully uninstalled Pyblish Mindbender!")


def is_installed():
    """Return state of installation

    Returns:
        True if installed, False otherwise

    """

    return self._is_installed


class Loader(object):
    families = list()

    def process(self, asset, subset, version, representation):
        pass


def discover_loaders():
    """Find and return available loaders

    """

    loaders = dict()

    # Include plug-ins from registered paths
    for path in _registered_loader_paths:
        path = os.path.normpath(path)

        assert os.path.isdir(path), "%s is not a directory" % path

        for fname in os.listdir(path):
            abspath = os.path.join(path, fname)

            if not os.path.isfile(abspath):
                continue

            mod_name, mod_ext = os.path.splitext(fname)

            if not mod_ext == ".py":
                continue

            module = types.ModuleType(mod_name)
            module.__file__ = abspath

            try:
                with open(abspath) as f:
                    six.exec_(f.read(), module.__dict__)

                # Store reference to original module, to avoid
                # garbage collection from collecting it's global
                # imports, such as `import os`.
                sys.modules[mod_name] = module

            except Exception as err:
                print("Skipped: \"%s\" (%s)", mod_name, err)
                continue

            for plugin in loaders_from_module(module):
                if plugin.__name__ in loaders:
                    print("Duplicate plug-in found: %s", plugin)
                    continue

                loaders[plugin.__name__] = plugin

    return list(loaders.values())


def loaders_from_module(module):
    """Return plug-ins from module

    Arguments:
        module (types.ModuleType): Imported module from which to
            parse valid Pyblish plug-ins.

    Returns:
        List of plug-ins, or empty list if none is found.

    """

    loaders = list()

    for name in dir(module):

        # It could be anything at this point
        obj = getattr(module, name)

        if not inspect.isclass(obj):
            continue

        if not issubclass(obj, Loader):
            continue

        loaders.append(obj)

    return loaders


def register_loader_path(path):
    path = os.path.normpath(path)
    _registered_loader_paths.add(path)


def registered_loader_paths():
    return list(_registered_loader_paths)


def deregister_loader_path(path):
    _registered_loader_paths.remove(path)


def ls(silos=None):
    """List available assets

    Return a list of available assets.

    The interface of this function, along with its schema, is designed
    to facilitate a potential transition into database-driven queries.

    Arguments:
        silo (str, optional): Path to asset silo, relative the currently
            registered silo, unless absolute. Defaults to an empty string.

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

    silos = silos or registered_silos()

    assert isinstance(silos, list), (
        "Argument `silos` must be a list of strings."
    )

    for silo in silos:
        assetsdir = (
            silo if os.path.isabs(silo)
            else os.path.join(registered_root(), silo)
        )

        assert assetsdir is not None, ("No registered root.")

        for asset in lib.listdir(assetsdir):
            assetdir = os.path.join(assetsdir, asset)
            publishdir = lib.format_shared_dir(assetdir)

            asset_entry = {
                "schema": "mindbender-core:asset-1.0",
                "name": asset,
                "subsets": list()
            }

            for subset in lib.listdir(publishdir):
                subsetdir = os.path.join(publishdir, subset)

                subset_entry = {
                    "schema": "mindbender-core:subset-1.0",
                    "name": subset,
                    "versions": list(),
                }

                asset_entry["subsets"].append(subset_entry)

                for version in lib.listdir(subsetdir):
                    versiondir = os.path.join(subsetdir, version)
                    fname = os.path.join(versiondir, ".metadata.json")

                    try:
                        with open(fname) as f:
                            version_entry = json.load(f)

                    except IOError:
                        self.log.warning("\"%s\" not found." % fname)
                        continue

                    if version_entry.get("schema") != ("mindbender-core"
                                                       ":version-1.0"):
                        self.log.warning("\"%s\" unsupported schema." % fname)
                        continue

                    subset_entry["versions"].append(version_entry)

                # Sort versions by integer
                subset_entry["versions"].sort(key=lambda v: v["version"])

            schema.validate(asset_entry, "asset")

            yield asset_entry


def _parse_query(query):
    """Parse a search query

    Arguments:
        query (str): Formatted string,
            e.g. "{asset}/{subset}/{version}.{representation}"
            e.g. "<str>/<str>/<int>.<str>"
            e.g. "Bruce/modelDefault/3.ma"

    Raises:
        SyntaxError on invalid query string

    Example:
        >>> result = _parse_query("Bruce/modelDefault/3.ma")
        >>> assert result[0] == "Bruce"
        >>> assert result[1] == "modelDefault"
        >>> assert result[2] == 3
        >>> assert result[3] == ".ma"
        >>> _parse_query("Wrong <")
        Traceback (most recent call last):
        ...
        SyntaxError: Invalid syntax: {asset}/{subset}/{version}.{repr}

    """

    try:
        asset, subset, _ = query.split("/")
        version, representation = _.split(".")
    except ValueError:
        raise SyntaxError("Invalid syntax: {asset}/{subset}/{version}.{repr}")

    representation = "." + representation

    try:
        version = int(version)
    except ValueError:
        raise SyntaxError("Version must be a number.")

    return asset, subset, version, representation


def search(query, root=None):
    """Search interface to ls()

    Arguments:
        query (str): Formatted string,
            e.g. "{asset}/{subset}/{version}.{representation}"
        root (str, optional): Subdirectory within which to search,
            defaults to "assets"

    """

    asset, subset, version, representation = _parse_query(query)

    for asset_ in ls(root or "assets"):
        if asset != asset_["name"]:
            continue

        for subset_ in asset_["subsets"]:
            if subset != subset_["name"]:
                continue

            try:
                version_ = subset_["versions"][
                    version - 1 if version > 0
                    else version
                ]

            except IndexError:
                continue

            for representation_ in version_["representations"]:
                if representation_["format"] != representation:
                    continue

                yield {
                    "schema": "mindbender-core:result-1.0",
                    "asset": asset_,
                    "subset": subset_,
                    "version": version_,
                    "representation": representation_
                }


def any_representation(version):
    """Pick any compatible representation.

    Arguments:
        version ("mindbender-core:version-1.0"): Version from which
            to pick a representation, based on currently registered formats.

    """

    supported_formats = registered_formats()

    try:
        representation = next(
            rep for rep in version["representations"]
            if rep["format"] in supported_formats
        )

    except StopIteration:
        formats = list(r["format"] for r in version["representations"])
        raise ValueError(
            "No supported representations.\n\n"
            "Available representations:\n%s\n\n"
            "Supported representations:\n%s"
            % ("\n- ".join(formats),
               "\n- ".join(supported_formats))
        )

    return representation


@contextlib.contextmanager
def fixture(assets=["Asset1"], subsets=["animRig"], versions=1):
    """Build transient fixture of `assets` and `versions`

    Generate a temporary fixture of customisable assets
    with current metadata schema. This function is intended
    for use in tests and tutorials.

    Arguments:
        assets (list, optional): Names of assets to create,
            defaults to one asset named "Asset1"
        subsets (int, optional): Number of subsets for each asset,
            defaults to 1 subset.
        versions (list, optional): Number of versions of each subset,
            defaults to 1 version.

    Thread Safety:
        This function modifies globals state and is
        therefore not thread-safe.

    Usage:
        >>> with fixture(assets=["MyAsset1"]):
        ...    for asset in ls(["assets"]):
        ...       assert asset["name"] == "MyAsset1"
        ...

    """

    tempdir = tempfile.mkdtemp()
    assetsdir = os.path.join(tempdir, "assets")

    for asset in assets:
        assetdir = os.path.join(assetsdir, asset)
        shareddir = lib.format_shared_dir(assetdir)
        os.makedirs(shareddir)

        for subset in subsets:
            subsetdir = os.path.join(shareddir, subset)
            os.makedirs(subsetdir)

            for version in range(versions):
                version = lib.format_version(version + 1)
                versiondir = os.path.join(subsetdir, version)
                os.makedirs(versiondir)

                fname = os.path.join(versiondir, asset + ".ma")
                open(fname, "w").close()  # touch

                fname = os.path.join(versiondir, ".metadata.json")

                with open(fname, "w") as f:
                    json.dump({
                        "schema": "mindbender-core:version-1.0",
                        "version": lib.parse_version(version),
                        "path": versiondir,
                        "time": "",
                        "families": ["mindbender.model"],
                        "author": "mottosso",
                        "source": os.path.join(
                            "{project}",
                            "maya",
                            "scenes",
                            "scene.ma"
                        ),
                        "representations": [
                            {
                                "schema": ("mindbender-core:"
                                           "representation-1.0"),
                                "format": ".ma",
                                "path": os.path.join(
                                    "{dirname}",
                                    "%s{format}" % asset
                                ),
                            },
                        ]
                    }, f)

    # Keep track of original root
    _ = _registered_root["_"]

    try:
        _registered_root["_"] = tempdir
        yield tempdir
    finally:
        _registered_root["_"] = _
        shutil.rmtree(tempdir)


def register_root(path):
    """Register currently active root"""
    self.log.info("Registering root: %s" % path)
    _registered_root["_"] = path


def registered_root():
    """Return currently registered root"""
    return (
        _registered_root["_"] or
        os.getenv("MINDBENDER_ROOT") or ""
    ).replace("\\", "/")


def register_format(format):
    """Register a supported format

    A supported format is used to determine which of any available
    representations are relevant to the currently registered host.

    """

    _registered_formats.append(format)


def deregister_format(format):
    """Deregister a supported format"""
    _registered_formats.remove(format)


def register_host(host):
    """Register a new host for the current process

    A majority of this function relates to validating
    the registered host. No host may be registered unless
    it fulfils the required interface, as specified in the
    Host API documentation.

    Arguments:
        host (ModuleType): A module implementing the
            Host API interface. See the Host API
            documentation for details on what is
            required, or browse the source code.

    """

    # Required signatures for each member
    signatures = {
        "load": [
            "asset",
            "subset",
            "version",
            "representation"
        ],
        "create": [
            "name",
            "family",
            "options"
        ],
        "ls": [
        ],
        "update": [
            "container",
            "version"
        ],
        "remove": [
            "container"
        ],

    }

    missing = list()
    invalid = list()
    success = True

    for member in signatures:
        if not hasattr(host, member):
            missing.append(member)
            success = False

        else:
            attr = getattr(host, member)
            signature = inspect.getargspec(attr)[0]
            required_signature = signatures[member]

            assert isinstance(signature, list)
            assert isinstance(required_signature, list)

            if not all(member in signature
                       for member in required_signature):
                invalid.append({
                    "member": member,
                    "signature": ", ".join(signature),
                    "required": ", ".join(required_signature)
                })
                success = False

    if not success:
        report = list()

        if missing:
            report.append(
                "Incomplete interface for host: '%s'\n"
                "Missing: %s" % (host, ", ".join(
                    "'%s'" % member for member in missing))
            )

        if invalid:
            report.append(
                "'%s': One or more members were found, but didn't "
                "have the right argument signature." % host.__name__
            )

            for member in invalid:
                report.append(
                    "     Found: {member}({signature})".format(**member)
                )
                report.append(
                    "  Expected: {member}({required})".format(**member)
                )

        raise ValueError("\n".join(report))

    else:
        _registered_host["_"] = host


def register_plugins():
    """Register accompanying plugins"""
    module_path = sys.modules[__name__].__file__
    package_path = os.path.dirname(module_path)
    plugins_path = os.path.join(package_path, "plugins")
    api.register_plugin_path(plugins_path)


def deregister_plugins():
    module_path = sys.modules[__name__].__file__
    package_path = os.path.dirname(module_path)
    plugins_path = os.path.join(package_path, "plugins")
    api.deregister_plugin_path(plugins_path)


def register_silo(name):
    _registered_silos.add(name)


def registered_silos():
    return (
        list(_registered_silos) or
        os.getenv("MINDBENDER_SILO", "").split()
    )


def register_data(key, value, help=None):
    """Register new default attribute

    Arguments:
        key (str): Name of data
        value (object): Arbitrary value of data
        help (str, optional): Briefly describe

    """

    _registered_data[key] = value


def deregister_data(key):
    _registered_data.pop(key)


def register_family(name,
                    label=None,
                    data=None,
                    help=None,
                    loader=None):
    """Register family and attributes for family

    Arguments:
        name (str): Name of family, e.g. mindbender.model
        label (str): Nice name for family, e.g. Model
        data (dict, optional): Additional data, see
            :func:`register_data` for docstring on members
        help (str, optional): Briefly describe this family

    """

    _registered_families[name] = {
        "name": name,
        "label": label,
        "data": data or {},
        "help": help or "",
        "loader": loader
    }


def deregister_family(name):
    _registered_families.pop(name)


def registered_formats():
    return _registered_formats[:]


def registered_families():
    return _registered_families.copy()


def registered_data():
    return _registered_data.copy()


def registered_host():
    return _registered_host["_"]


def deregister_host():
    _registered_host["_"] = default_host()


def default_host():
    """A default host, in place of anything better

    This may be considered as reference for the
    interface a host must implement. It also ensures
    that the system runs, even when nothing is there
    to support it.

    """

    host = types.ModuleType("defaultHost")

    def ls():
        return list()

    def load(asset, subset, version=-1, representation=None):
        return None

    def create(name, family, nodes=None):
        return "instanceFromDefaultHost"

    def remove(container):
        print("Removing '%s' from defaultHost.." % container["name"])

    host.__dict__.update({
        "ls": ls,
        "load": load,
        "create": create,
        "remove": remove,
    })

    return host


def debug_host():
    """A debug host, useful to debugging features that depend on a host"""
    host = types.ModuleType("debugHost")

    def ls():
        return list()

    def load(asset, subset, version=-1, representation=None):
        sys.stdout.write(json.dumps({
            "asset": asset,
            "subset": subset,
            "version": version,
            "representation": representation
        }, indent=4) + "\n"),

        return None

    def create(name, family, options=None):
        sys.stdout.write(json.dumps({
            "name": name,
            "family": family,
        }, indent=4))
        return "instanceFromDebugHost"

    def update(container, version=-1):
        print("Grading '{name}' from '{from_}' to '{to_}'".format(
            name=container["name"],
            from_=container["version"],
            to_=version
        ))

    def remove(container):
        print("Removing '%s' from debugHost.." % container["name"])

    host.__dict__.update({
        "ls": ls,
        "load": load,
        "create": create,
        "update": update,
        "remove": remove,
    })

    return host
