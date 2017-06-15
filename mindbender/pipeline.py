import os
import sys
import types
import logging
import inspect
import importlib

from . import (
    io,
    lib,

    _registered_host,
    _registered_root,
    _registered_formats,
    _registered_plugins,
    _registered_plugin_paths,
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

    project = os.environ["MINDBENDER_PROJECT"]
    lib.logger.info("Activating %s.." % project)

    io.install()
    io.activate_project(project)

    config = find_config()

    # Optional host install function
    if hasattr(host, "install"):
        host.install(config)

    register_host(host)

    config.install()

    self._is_installed = True
    self.log.info("Successfully installed Pyblish Mindbender!")


def find_config():
    lib.logger.info("Finding configuration for project..")

    project = io.find_one({"type": "project"})
    config = project["config"].get("name")

    if not config:
        config = os.getenv("MINDBENDER_CONFIG")

    if not config:
        raise EnvironmentError("No configuration found in "
                               "the project nor environment")

    lib.logger.info("Found %s, loading.." % config)
    return importlib.import_module(config)


def uninstall():
    try:
        registered_host().uninstall()
    except AttributeError:
        pass

    deregister_host()

    io.uninstall()

    self.log.info("Successfully uninstalled Pyblish Mindbender!")


def is_installed():
    """Return state of installation

    Returns:
        True if installed, False otherwise

    """

    return self._is_installed


@lib.log
class Loader(list):
    """Load representation into host application

    Arguments:
        context (dict): mindbender-core:context-1.0
        name (str, optional): Use pre-defined name
        namespace (str, optional): Use pre-defined namespace

    """

    families = list()
    representations = list()

    def __init__(self, context):
        template = context["project"]["config"]["template"]["publish"]

        data = {
            key: value["name"]
            for key, value in context.items()
        }

        data["root"] = registered_root()
        data["silo"] = context["asset"]["silo"]

        fname = template.format(**data)

        self.fname = fname

    def process(self, name, namespace, context):
        pass

    def post_process(self, name, namespace, context):
        pass


@lib.log
class Creator(object):
    name = None
    label = None
    family = None

    def __init__(self, name, asset, options=None, data=None):
        self.name = name or self.name
        self.options = options

        # Default data
        self.data = dict({
            "id": "pyblish.mindbender.instance",
            "family": self.family,
            "asset": asset,
            "subset": name
        }, **(data or {}))

    def process(self):
        pass


def discover(superclass):
    """Find and return subclasses of `superclass`"""

    registered = _registered_plugins.get(superclass, list())
    plugins = dict()

    # Include plug-ins from registered paths
    for path in _registered_plugin_paths.get(superclass, list()):
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

            for plugin in plugin_from_module(superclass, module):
                if plugin.__name__ in plugins:
                    print("Duplicate plug-in found: %s", plugin)
                    continue

                plugins[plugin.__name__] = plugin

    for plugin in registered:
        if plugin.__name__ in plugins:
            print("Warning: Overwriting %s" % plugin.__name__)
        plugins[plugin.__name__] = plugin

    return sorted(plugins.values(), key=lambda Plugin: Plugin.__name__)


def plugin_from_module(superclass, module):
    """Return plug-ins from module

    Arguments:
        superclass (superclass): Superclass of subclasses to look for
        module (types.ModuleType): Imported module from which to
            parse valid Pyblish plug-ins.

    Returns:
        List of plug-ins, or empty list if none is found.

    """

    types = list()

    for name in dir(module):

        # It could be anything at this point
        obj = getattr(module, name)

        if not inspect.isclass(obj):
            continue

        if not issubclass(obj, superclass):
            continue

        types.append(obj)

    return types


def register_plugin(superclass, obj):
    if superclass not in _registered_plugins:
        _registered_plugins[superclass] = list()

    if obj not in _registered_plugins[superclass]:
        _registered_plugins[superclass].append(obj)


def register_plugin_path(superclass, path):
    if superclass not in _registered_plugin_paths:
        _registered_plugin_paths[superclass] = list()

    path = os.path.normpath(path)
    if path not in _registered_plugin_paths[superclass]:
        _registered_plugin_paths[superclass].append(path)


def registered_plugin_paths():
    # Prohibit editing in-place
    duplicate = {
        superclass: paths[:]
        for superclass, paths in _registered_plugin_paths.items()
    }

    return duplicate


def deregister_plugin(superclass, plugin):
    _registered_plugins[superclass].remove(plugin)


def deregister_plugin_path(superclass, path):
    _registered_plugin_paths[superclass].remove(path)


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
            "name",
            "family",
            "asset",
            "options",
            "data"
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

    # for member in signatures:
    #     if not hasattr(host, member):
    #         missing.append(member)
    #         success = False

    #     else:
    #         attr = getattr(host, member)
    #         signature = inspect.getargspec(attr)[0]
    #         required_signature = signatures[member]

    #         assert isinstance(signature, list)
    #         assert isinstance(required_signature, list)

    #         if not all(member in signature
    #                    for member in required_signature):
    #             invalid.append({
    #                 "member": member,
    #                 "signature": ", ".join(signature),
    #                 "required": ", ".join(required_signature)
    #             })
    #             success = False

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


def registered_formats():
    return _registered_formats[:]


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

    def load(representation=None,
             name=None,
             namespace=None,
             post_process=None,
             preset=None):
        return None

    def create(family):
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

    def load(representation=None,
             name=None,
             namespace=None,
             post_process=None,
             preset=None):
        sys.stdout.write(pformat({
            "representation": representation
        }) + "\n"),

        return None

    def create(name, asset, family, options=None, data=None):
        sys.stdout.write(pformat({
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
