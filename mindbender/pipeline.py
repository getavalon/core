import os
import sys
import types
import logging
import inspect

from pyblish import api

from . import (
    io,

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

    missing = list()
    for key in ("MINDBENDER_PROJECT", "MINDBENDER_ASSET"):
        if key not in os.environ:
            missing.append(key)

    assert not missing, (
        "%s missing from environment" % ", ".join(missing)
    )

    # Optional host install function
    if hasattr(host, "install"):
        host.install()

    register_host(host)
    register_plugins()

    io.install()
    io.activate_project(os.environ["MINDBENDER_PROJECT"])

    self._is_installed = True
    self.log.info("Successfully installed Pyblish Mindbender!")


def uninstall():
    try:
        registered_host().uninstall()
    except AttributeError:
        pass

    deregister_host()
    deregister_plugins()

    io.uninstall()

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
            "representation"
        ],
        "create": [
            "asset",
            "subset",
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

    def load(representation=None):
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
    from pprint import pformat

    host = types.ModuleType("debugHost")

    def ls():
        containers = [
            {
                "schema": "mindbender-core:container-1.0",
                "name": "Bruce01",
                "asset": "Bruce",
                "subset": "rigDefault",
                "version": 3,
                "silo": "assets",
            },
            {
                "schema": "mindbender-core:container-1.0",
                "name": "Bruce02",
                "asset": "Bruce",
                "subset": "modelDefault",
                "version": 2,
                "silo": "assets",
            }
        ]

        for container in containers:
            yield container

    def load(representation=None):
        sys.stdout.write(pformat({
            "representation": representation
        }) + "\n"),

        return None

    def create(name, family, options=None):
        sys.stdout.write(pformat({
            "name": name,
            "family": family,
        }))
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
