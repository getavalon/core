"""Core pipeline functionality"""

import os
import sys
import json
import types
import logging
import weakref
import inspect
import traceback
import importlib

from . import (
    io,
    lib,

    Session,

    _registered_host,
    _registered_root,
    _registered_config,
    _registered_plugins,
    _registered_plugin_paths,
    _registered_event_handlers,
)

from .vendor import six

self = sys.modules[__name__]
self._is_installed = False
self._config = None

log = logging.getLogger(__name__)


def install(host):
    """Install `host` into the running Python session.

    Arguments:
        host (module): A Python module containing the Avalon
            avalon host-interface.

    """

    io.install()

    missing = list()
    for key in ("AVALON_PROJECT", "AVALON_ASSET"):
        if key not in Session:
            missing.append(key)

    assert not missing, (
        "%s missing from environment, %s" % (
            ", ".join(missing),
            json.dumps(Session, indent=4, sort_keys=True)
        ))

    project = Session["AVALON_PROJECT"]
    log.info("Activating %s.." % project)

    config = find_config()

    # Optional host install function
    if hasattr(host, "install"):
        host.install(config)

    register_host(host)
    register_config(config)

    config.install()

    self._is_installed = True
    self._config = config
    log.info("Successfully installed Avalon!")


def find_config():
    log.info("Finding configuration for project..")

    config = Session["AVALON_CONFIG"]

    if not config:
        raise EnvironmentError("No configuration found in "
                               "the project nor environment")

    log.info("Found %s, loading.." % config)
    return importlib.import_module(config)


def uninstall():
    """Undo all of what `install()` did"""
    try:
        registered_host().uninstall()
    except AttributeError:
        pass

    try:
        registered_config().uninstall()
    except AttributeError:
        pass

    deregister_host()
    deregister_config()

    io.uninstall()

    log.info("Successfully uninstalled Avalon!")


def is_installed():
    """Return state of installation

    Returns:
        True if installed, False otherwise

    """

    return self._is_installed


def publish():
    """Shorthand to publish from within host"""
    from pyblish import util
    return util.publish()


@lib.log
class Loader(list):
    """Load representation into host application

    Arguments:
        context (dict): avalon-core:context-1.0
        name (str, optional): Use pre-defined name
        namespace (str, optional): Use pre-defined namespace

    .. versionadded:: 4.0
       This class was introduced

    """

    families = list()
    representations = list()
    order = 0

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

    def load(self, context, name=None, namespace=None, data=None):
        """Load asset via database

        Arguments:
            context (dict): Full parenthood of representation to load
            name (str, optional): Use pre-defined name
            namespace (str, optional): Use pre-defined namespace
            data (dict, optional): Additional settings dictionary

        """
        pass

    def update(self, container, representation):
        """Update `container` to `representation`

        Arguments:
            container (avalon-core:container-1.0): Container to update,
                from `host.ls()`.
            representation (dict): Update the container to this representation.

        """
        pass

    def remove(self, container):
        """Remove a container
        
        Arguments:
            container (avalon-core:container-1.0): Container to remove,
                from `host.ls()`.
                
        Returns:
            bool: Whether the container was deleted
            
        """
        return False


@lib.log
class Creator(object):
    """Determine how assets are created"""
    name = None
    label = None
    family = None

    def __init__(self, name, asset, options=None, data=None):
        self.name = name or self.name
        self.options = options

        # Default data
        self.data = dict({
            "id": "pyblish.avalon.instance",
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
            # Ignore files which start with underscore
            if fname.startswith("_"):
                continue

            mod_name, mod_ext = os.path.splitext(fname)
            if not mod_ext == ".py":
                continue

            abspath = os.path.join(path, fname)
            if not os.path.isfile(abspath):
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
            parse valid Avalon plug-ins.

    Returns:
        List of plug-ins, or empty list if none is found.

    """

    types = list()

    def recursive_bases(klass):
        r = []
        bases = klass.__bases__
        r.extend(bases)
        for base in bases:
            r.extend(recursive_bases(base))
        return r

    for name in dir(module):

        # It could be anything at this point
        obj = getattr(module, name)

        if not inspect.isclass(obj):
            continue

        # These are subclassed from nothing, not even `object`
        if not len(obj.__bases__) > 0:
            continue

        # Use string comparison rather than `issubclass`
        # in order to support reloading of this module.
        bases = recursive_bases(obj)
        if not any(base.__name__ == superclass.__name__ for base in bases):
            continue

        types.append(obj)

    return types


def on(event, callback):
    """Call `callback` on `event`

    Register `callback` to be run when `event` occurs.

    Example:
        >>> def on_init():
        ...    print("Init happened")
        ...
        >>> on("init", on_init)
        >>> del on_init

    Arguments:
        event (str): Name of event
        callback (callable): Any callable

    """

    if event not in _registered_event_handlers:
        _registered_event_handlers[event] = weakref.WeakSet()

    events = _registered_event_handlers[event]
    events.add(callback)


def before(event, callback):
    """Convenience to `on()` for before-events"""
    on("before_" + event, callback)


def after(event, callback):
    """Convenience to `on()` for after-events"""
    on("after_" + event, callback)


def emit(event, args=None):
    """Trigger an `event`

    Example:
        >>> def on_init():
        ...    print("Init happened")
        ...
        >>> on("init", on_init)
        >>> emit("init")
        Init happened
        >>> del on_init

    Arguments:
        event (str): Name of event
        args (list, optional): List of arguments passed to callback

    """

    callbacks = _registered_event_handlers.get(event, set())
    args = args or list()

    for callback in callbacks:
        try:
            callback(*args)
        except Exception:
            log.debug(traceback.format_exc())


def register_plugin(superclass, obj):
    """Register an individual `obj` of type `superclass`

    Arguments:
        superclass (type): Superclass of plug-in
        obj (object): Subclass of `superclass`

    """

    if superclass not in _registered_plugins:
        _registered_plugins[superclass] = list()

    if obj not in _registered_plugins[superclass]:
        _registered_plugins[superclass].append(obj)


def register_plugin_path(superclass, path):
    """Register a directory of one or more plug-ins

    Arguments:
        superclass (type): Superclass of plug-ins to look for during discovery
        path (str): Absolute path to directory in which to discover plug-ins

    """

    if superclass not in _registered_plugin_paths:
        _registered_plugin_paths[superclass] = list()

    path = os.path.normpath(path)
    if path not in _registered_plugin_paths[superclass]:
        _registered_plugin_paths[superclass].append(path)


def registered_plugin_paths():
    """Return all currently registered plug-in paths"""

    # Prohibit editing in-place
    duplicate = {
        superclass: paths[:]
        for superclass, paths in _registered_plugin_paths.items()
    }

    return duplicate


def deregister_plugin(superclass, plugin):
    """Oppsite of `register_plugin()`"""
    _registered_plugins[superclass].remove(plugin)


def deregister_plugin_path(superclass, path):
    """Oppsite of `register_plugin_path()`"""
    _registered_plugin_paths[superclass].remove(path)


def register_root(path):
    """Register currently active root"""
    log.info("Registering root: %s" % path)
    _registered_root["_"] = path


def registered_root():
    """Return currently registered root"""
    return os.path.normpath(
        _registered_root["_"] or
        Session.get("AVALON_PROJECTS") or ""
    )


def register_host(host):
    """Register a new host for the current process

    Arguments:
        host (ModuleType): A module implementing the
            Host API interface. See the Host API
            documentation for details on what is
            required, or browse the source code.

    """
    signatures = {
        "ls": []
    }

    _validate_signature(host, signatures)
    _registered_host["_"] = host


def register_config(config):
    """Register a new config for the current process

    Arguments:
        config (ModuleType): A module implementing the Config API.

    """

    signatures = {
        "install": [],
        "uninstall": [],
    }

    _validate_signature(config, signatures)
    _registered_config["_"] = config


def _validate_signature(module, signatures):
    # Required signatures for each member

    missing = list()
    invalid = list()
    success = True

    for member in signatures:
        if not hasattr(module, member):
            missing.append(member)
            success = False

        else:
            attr = getattr(module, member)
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
                "Incomplete interface for module: '%s'\n"
                "Missing: %s" % (module, ", ".join(
                    "'%s'" % member for member in missing))
            )

        if invalid:
            report.append(
                "'%s': One or more members were found, but didn't "
                "have the right argument signature." % module.__name__
            )

            for member in invalid:
                report.append(
                    "     Found: {member}({signature})".format(**member)
                )
                report.append(
                    "  Expected: {member}({required})".format(**member)
                )

        raise ValueError("\n".join(report))


def deregister_config():
    """Undo `register_config()`"""
    _registered_config["_"] = None


def registered_config():
    """Return currently registered config"""
    return _registered_config["_"]


def registered_host():
    """Return currently registered host"""
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

    host.__dict__.update({
        "ls": ls
    })

    return host


def debug_host():
    """A debug host, useful to debugging features that depend on a host"""

    host = types.ModuleType("debugHost")

    def ls():
        containers = [
            {
                "representation": "ee-ft-a-uuid1",
                "schema": "avalon-core:container-1.0",
                "name": "Bruce01",
                "objectName": "Bruce01_node",
                "namespace": "_bruce01_",
                "version": 3,
            },
            {
                "representation": "aa-bc-s-uuid2",
                "schema": "avalon-core:container-1.0",
                "name": "Bruce02",
                "objectName": "Bruce01_node",
                "namespace": "_bruce02_",
                "version": 2,
            }
        ]

        for container in containers:
            yield container

    host.__dict__.update({
        "ls": ls
    })

    return host


def create(name, asset, family, options=None, data=None):
    """Create a new instance

    Associate nodes with a subset and family. These nodes are later
    validated, according to their `family`, and integrated into the
    shared environment, relative their `subset`.

    Data relative each family, along with default data, are imprinted
    into the resulting objectSet. This data is later used by extractors
    and finally asset browsers to help identify the origin of the asset.

    Arguments:
        name (str): Name of subset
        asset (str): Name of asset
        family (str): Name of family
        options (dict, optional): Additional options from GUI
        data (dict, optional): Additional data from GUI

    Raises:
        NameError on `subset` already exists
        KeyError on invalid dynamic property
        RuntimeError on host error

    Returns:
        Name of instance

    """

    host = registered_host()

    plugins = list()
    for Plugin in discover(Creator):
        has_family = family == Plugin.family

        if not has_family:
            continue

        Plugin.log.info(
            "Creating '%s' with '%s'" % (name, Plugin.__name__)
        )

        try:
            plugin = Plugin(name, asset, options, data)

            with host.maintained_selection():
                instance = plugin.process()
        except Exception as e:
            log.warning(e)
            continue

        plugins.append(plugin)

    assert plugins, "No Creator plug-ins were run, this is a bug"
    return instance


def _get_representation_context(representation):

    assert representation is not None, "This is a bug"

    if isinstance(representation, (six.string_types, io.ObjectId)):
        representation = io.find_one(
            {"_id": io.ObjectId(str(representation))})

    version, subset, asset, project = io.parenthood(representation)

    assert all([representation, version, subset, asset, project]), (
        "This is a bug"
    )

    context = {
        "project": project,
        "asset": asset,
        "subset": subset,
        "version": version,
        "representation": representation,
    }

    return context


def _make_backwards_compatible_loader(Loader):
    """Convert a old-style Loaders with `process` method to new-style Loader
    
    This will make a dynamic class inheriting the old-style loader together
    with a BackwardsCompatibleLoader. This backwards compatible loader will
    expose `load`, `remove` and `update` in the same old way for Maya loaders.
    
    The `load` method will then call `process()` just like before.
    
    """

    # Assume new-style loader when no `process` method is exposed
    # then we don't swap the loader with a backwards compatible one.
    if not hasattr(Loader, "process"):
        return Loader

    log.warning("Making loader backwards compatible: %s", Loader.__name__)
    from avalon.maya.compat import BackwardsCompatibleLoader
    return type(Loader.__name__, (BackwardsCompatibleLoader, Loader), {})


def load(Loader, representation, namespace=None, name=None, data=None):

    Loader = _make_backwards_compatible_loader(Loader)

    context = _get_representation_context(representation)

    # Ensure data is a dictionary when no explicit data provided
    if data is None:
        data = dict()
    assert isinstance(data, dict), "Data must be a dictionary"

    # Fallback to subset when name is None
    if name is None:
        name = context['subset']['name']

    # todo(roy): Ensure the Loader is valid for the representation

    log.info(
        "Running '%s' on '%s'" % (Loader.__name__, context['asset']["name"])
    )

    loader = Loader(context)
    return loader.load(context=context,
                       name=name,
                       namespace=namespace,
                       data=data)


def _get_container_loader(container):
    """Return the Loader corresponding to the container"""

    loader = container['loader']
    for Plugin in discover(Loader):

        # TODO: Ensure the loader is valid
        if Plugin.__name__ == loader:
            return Plugin


def remove(container):
    """Remove a container"""

    Loader = _get_container_loader(container)
    if not Loader:
        raise RuntimeError("Can't remove container. See log for details.")

    Loader = _make_backwards_compatible_loader(Loader)

    loader = Loader(_get_representation_context(container['representation']))
    return loader.remove(container)


def update(container, version=-1):
    """Update a container"""

    # Compute the different version from 'representation'
    current_representation = io.find_one({
        "_id": io.ObjectId(container["representation"])
    })

    assert current_representation is not None, "This is a bug"

    current_version, subset, asset, project = io.parenthood(
        current_representation)

    if version == -1:
        new_version = io.find_one({
            "type": "version",
            "parent": subset["_id"]
        }, sort=[("name", -1)])
    else:
        new_version = io.find_one({
            "type": "version",
            "parent": subset["_id"],
            "name": version,
        })

    new_representation = io.find_one({
        "type": "representation",
        "parent": new_version["_id"],
        "name": current_representation["name"]
    })

    assert new_version is not None, "This is a bug"

    # Run update on the Loader for this container
    Loader = _get_container_loader(container)
    if not Loader:
        raise RuntimeError("Can't update container. See log for details.")

    Loader = _make_backwards_compatible_loader(Loader)

    loader = Loader(_get_representation_context(container['representation']))
    return loader.update(container, new_representation)


def get_representation_path(representation):
    """Get filename from representation id"""

    version_, subset, asset, project = io.parenthood(representation)
    template_publish = project["config"]["template"]["publish"]
    return template_publish.format(**{
        "root": registered_root(),
        "project": project["name"],
        "asset": asset["name"],
        "silo": asset["silo"],
        "subset": subset["name"],
        "version": version_["name"],
        "representation": representation["name"],
    })
