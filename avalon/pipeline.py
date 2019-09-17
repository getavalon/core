"""Core pipeline functionality"""

import os
import sys
import json
import errno
import types
import shutil
import getpass
import logging
import weakref
import inspect
import traceback
import importlib

from collections import OrderedDict

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
self.data = {}

log = logging.getLogger(__name__)


AVALON_CONTAINER_ID = "pyblish.avalon.container"


class IncompatibleLoaderError(ValueError):
    """Error when Loader is incompatible with a representation."""
    pass


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
    config = registered_config()

    try:
        registered_host().uninstall(config)
    except AttributeError:
        pass

    try:
        config.uninstall()
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
        representation = context['representation']
        self.fname = get_representation_path(representation)

    def load(self, context, name=None, namespace=None, options=None):
        """Load asset via database

        Arguments:
            context (dict): Full parenthood of representation to load
            name (str, optional): Use pre-defined name
            namespace (str, optional): Use pre-defined namespace
            options (dict, optional): Additional settings dictionary

        """
        raise NotImplementedError("Loader.load() must be "
                                  "implemented by subclass")

    def update(self, container, representation):
        """Update `container` to `representation`

        Arguments:
            container (avalon-core:container-1.0): Container to update,
                from `host.ls()`.
            representation (dict): Update the container to this representation.

        """
        raise NotImplementedError("Loader.update() must be "
                                  "implemented by subclass")

    def remove(self, container):
        """Remove a container

        Arguments:
            container (avalon-core:container-1.0): Container to remove,
                from `host.ls()`.

        Returns:
            bool: Whether the container was deleted

        """

        raise NotImplementedError("Loader.remove() must be "
                                  "implemented by subclass")


@lib.log
class Creator(object):
    """Determine how assets are created"""
    label = None
    family = None
    defaults = None

    def __init__(self, name, asset, options=None, data=None):
        self.name = name  # For backwards compatibility
        self.options = options

        # Default data
        self.data = OrderedDict()
        self.data["id"] = "pyblish.avalon.instance"
        self.data["family"] = self.family
        self.data["asset"] = asset
        self.data["subset"] = name
        self.data["active"] = True

        self.data.update(data or {})

    def process(self):
        pass


@lib.log
class Action(object):
    """A custom action available"""
    name = None
    label = None
    icon = None
    color = None
    order = 0

    def is_compatible(self, session):
        """Return whether the class is compatible with the Session."""
        return True

    def process(self, session, **kwargs):
        pass


class InventoryAction(object):
    """A custom action for the scene inventory tool

    If registered the action will be visible in the Right Mouse Button menu
    under the submenu "Actions".

    """

    label = None
    icon = None
    color = None
    order = 0

    @staticmethod
    def is_compatible(container):
        """Override function in a custom class

        This method is specifically used to ensure the action can operate on
        the container.

        Args:
            container(dict): the data of a loaded asset, see host.ls()

        Returns:
            bool
        """
        return bool(container.get("objectName"))

    def process(self, containers):
        """Override function in a custom class

        This method will receive all containers even those which are
        incompatible. It is advised to create a small filter along the lines
        of this example:

        valid_containers = filter(self.is_compatible(c) for c in containers)

        The return value will need to be a True-ish value to trigger
        the data_changed signal in order to refresh the view.

        You can return a list of container names to trigger GUI to select
        treeview items.

        You can return a dict to carry extra GUI options. For example:
            {
                "objectNames": [container names...],
                "options": {"mode": "toggle",
                            "clear": False}
            }
        Currently workable GUI options are:
            - clear (bool): Clear current selection before selecting by action.
                            Default `True`.
            - mode (str): selection mode, use one of these:
                          "select", "deselect", "toggle". Default is "select".

        Args:
            containers (list): list of dictionaries

        Return:
            bool, list or dict

        """
        return True


class Application(Action):
    """Default application launcher

    This is a convenience application Action that when "config" refers to a
    parsed application `.toml` this can launch the application.

    """

    config = None

    def is_compatible(self, session):
        required = ["AVALON_PROJECTS",
                    "AVALON_PROJECT",
                    "AVALON_SILO",
                    "AVALON_ASSET",
                    "AVALON_TASK"]
        missing = [x for x in required if x not in session]
        if missing:
            self.log.debug("Missing keys: %s" % (missing,))
            return False
        return True

    def environ(self, session):
        """Build application environment"""

        session = session.copy()
        session["AVALON_APP"] = self.config["application_dir"]
        session["AVALON_APP_NAME"] = self.name

        # Compute work directory
        project = io.find_one({"type": "project"})
        template = project["config"]["template"]["work"]
        workdir = _format_work_template(template, session)
        session["AVALON_WORKDIR"] = os.path.normpath(workdir)

        # Construct application environment from .toml config
        app_environment = self.config.get("environment", {})
        for key, value in app_environment.copy().items():
            if isinstance(value, list):
                # Treat list values as paths, e.g. PYTHONPATH=[]
                app_environment[key] = os.pathsep.join(value)

            elif isinstance(value, six.string_types):
                if lib.PY2:
                    # Protect against unicode in the environment
                    encoding = sys.getfilesystemencoding()
                    app_environment[key] = value.encode(encoding)
                else:
                    app_environment[key] = value
            else:
                log.error(
                    "%s: Unsupported environment reference in %s for %s"
                    % (value, self.name, key)
                )

        # Build environment
        env = os.environ.copy()
        env.update(session)
        app_environment = self._format(app_environment, **env)
        env.update(app_environment)

        return env

    def initialize(self, environment):
        """Initialize work directory"""
        # Create working directory
        workdir = environment["AVALON_WORKDIR"]
        workdir_existed = os.path.exists(workdir)
        if not workdir_existed:
            os.makedirs(workdir)
            self.log.info("Creating working directory '%s'" % workdir)

            # Create default directories from app configuration
            default_dirs = self.config.get("default_dirs", [])
            default_dirs = self._format(default_dirs, **environment)
            if default_dirs:
                self.log.debug("Creating default directories..")
                for dirname in default_dirs:
                    try:
                        os.makedirs(os.path.join(workdir, dirname))
                        self.log.debug(" - %s" % dirname)
                    except OSError as e:
                        # An already existing default directory is fine.
                        if e.errno == errno.EEXIST:
                            pass
                        else:
                            raise

        # Perform application copy
        for src, dst in self.config.get("copy", {}).items():
            dst = os.path.join(workdir, dst)
            # Expand env vars
            src, dst = self._format([src, dst], **environment)

            try:
                self.log.info("Copying %s -> %s" % (src, dst))
                shutil.copy(src, dst)
            except OSError as e:
                self.log.error("Could not copy application file: %s" % e)
                self.log.error(" - %s -> %s" % (src, dst))

    def launch(self, environment):

        executable = lib.which(self.config["executable"])
        if executable is None:
            raise ValueError(
                "'%s' not found on your PATH\n%s"
                % (self.config["executable"], os.getenv("PATH"))
            )

        args = self.config.get("args", [])
        return lib.launch(
            executable=executable,
            args=args,
            environment=environment,
            cwd=environment["AVALON_WORKDIR"]
        )

    def process(self, session, **kwargs):
        """Process the full Application action"""

        environment = self.environ(session)

        if kwargs.get("initialize", True):
            self.initialize(environment)

        if kwargs.get("launch", True):
            return self.launch(environment)

    def _format(self, original, **kwargs):
        """Utility recursive dict formatting that logs the error clearly."""

        try:
            return lib.dict_format(original, **kwargs)
        except KeyError as e:
            log.error(
                "One of the {variables} defined in the application "
                "definition wasn't found in this session.\n"
                "The variable was %s " % e
            )
            log.error(json.dumps(kwargs, indent=4, sort_keys=True))

            raise ValueError(
                "This is typically a bug in the pipeline, "
                "ask your developer.")


def discover(superclass):
    """Find and return subclasses of `superclass`"""

    registered = _registered_plugins.get(superclass, list())
    plugins = dict()

    # Include plug-ins from registered paths
    for path in _registered_plugin_paths.get(superclass, list()):
        for module in lib.modules_from_path(path):
            for plugin in plugin_from_module(superclass, module):
                if plugin.__name__ in plugins:
                    print("Duplicate plug-in found: %s" % plugin)
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
            log.warning(traceback.format_exc())


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
        "ls": ls,
        "open_file": lambda fname: None,
        "save_file": lambda fname: None,
        "current_file": lambda: os.path.expanduser("~/temp.txt"),
        "has_unsaved_changes": lambda: False,
        "work_root": lambda: os.path.expanduser("~/temp"),
        "file_extensions": lambda: ["txt"],
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
                print("Running %s" % plugin)
                instance = plugin.process()
        except Exception as e:
            log.warning(e)
            continue
        plugins.append(plugin)

    assert plugins, "No Creator plug-ins were run, this is a bug"
    return instance


def get_representation_context(representation):
    """Return parenthood context for representation.

    Args:
        representation (str or io.ObjectId or dict): The representation id
            or full representation as returned by the database.

    Returns:
        dict: The full representation context.

    """

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


def update_current_task(task=None, asset=None, app=None):
    """Update active Session to a new task work area.

    This updates the live Session to a different `asset`, `task` or `app`.

    Args:
        task (str): The task to set.
        asset (str): The asset to set.
        app (str): The app to set.

    Returns:
        dict: The changed key, values in the current Session.

    """

    mapping = {
        "AVALON_ASSET": asset,
        "AVALON_TASK": task,
        "AVALON_APP": app,
    }
    changed = {key: value for key, value in mapping.items() if value}
    if not changed:
        return

    # Update silo when asset changed
    if "AVALON_ASSET" in changed:
        asset_document = io.find_one({"name": changed["AVALON_ASSET"],
                                      "type": "asset"})
        assert asset_document, "Asset must exist"
        changed["AVALON_SILO"] = asset_document["silo"]

    # Compute work directory (with the temporary changed session so far)
    project = io.find_one({"type": "project"},
                          projection={"config.template.work": True})
    template = project["config"]["template"]["work"]
    _session = Session.copy()
    _session.update(changed)
    changed["AVALON_WORKDIR"] = _format_work_template(template, _session)

    parents = asset_document['data'].get('parents', [])
    hierarchy = ""
    if len(parents) > 0:
        hierarchy = os.path.sep.join(parents)
    changed['AVALON_HIERARCHY'] = hierarchy

    # Update the full session in one go to avoid half updates
    Session.update(changed)

    # Update the environment
    os.environ.update(changed)

    # Emit session change
    emit("taskChanged", changed.copy())

    return changed


def _format_work_template(template, session=None):
    """Return a formatted configuration template with a Session.

    Note: This *cannot* format the templates for published files since the
        session does not hold the context for a published file. Instead use
        `get_representation_path` to parse the full path to a published file.

    Args:
        template (str): The template to format.
        session (dict, Optional): The Session to use. If not provided use the
            currently active global Session.

    Returns:
        str: The fully formatted path.

    """
    if session is None:
        session = Session

    return template.format(**{
        "root": registered_root(),
        "project": session["AVALON_PROJECT"],
        "silo": session["AVALON_SILO"],
        "asset": session["AVALON_ASSET"],
        "task": session["AVALON_TASK"],
        "app": session["AVALON_APP"],

        # Optional
        "user": session.get("AVALON_USER", getpass.getuser()),
        "hierarchy": session.get("AVALON_HIERARCHY"),
    })


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


def load(Loader, representation, namespace=None, name=None, options=None,
         **kwargs):
    """Use Loader to load a representation.

    Args:
        Loader (Loader): The loader class to trigger.
        representation (str or io.ObjectId or dict): The representation id
            or full representation as returned by the database.
        namespace (str, Optional): The namespace to assign. Defaults to None.
        name (str, Optional): The name to assign. Defaults to subset name.
        options (dict, Optional): Additional options to pass on to the loader.

    Returns:
        The return of the `loader.load()` method.

    Raises:
        IncompatibleLoaderError: When the loader is not compatible with
            the representation.

    """

    Loader = _make_backwards_compatible_loader(Loader)
    context = get_representation_context(representation)

    # Ensure the Loader is compatible for the representation
    if not is_compatible_loader(Loader, context):
        raise IncompatibleLoaderError("Loader {} is incompatible with "
                                      "{}".format(Loader.__name__,
                                                  context["subset"]["name"]))

    # Ensure options is a dictionary when no explicit options provided
    if options is None:
        options = kwargs.get("data", dict())  # "data" for backward compat

    assert isinstance(options, dict), "Options must be a dictionary"

    # Fallback to subset when name is None
    if name is None:
        name = context["subset"]["name"]

    log.info(
        "Running '%s' on '%s'" % (Loader.__name__, context["asset"]["name"])
    )

    loader = Loader(context)
    return loader.load(context, name, namespace, options)


def _get_container_loader(container):
    """Return the Loader corresponding to the container"""

    loader = container["loader"]
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

    loader = Loader(get_representation_context(container["representation"]))
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

    assert new_version is not None, "This is a bug"

    new_representation = io.find_one({
        "type": "representation",
        "parent": new_version["_id"],
        "name": current_representation["name"]
    })

    # Run update on the Loader for this container
    Loader = _get_container_loader(container)
    if not Loader:
        raise RuntimeError("Can't update container. See log for details.")

    Loader = _make_backwards_compatible_loader(Loader)

    loader = Loader(get_representation_context(container["representation"]))
    return loader.update(container, new_representation)


def switch(container, representation):
    """Switch a container to representation

    Args:
        container (dict): container information
        representation (dict): representation data from document

    Returns:
        function call
    """

    # Get the Loader for this container
    Loader = _get_container_loader(container)
    if not Loader:
        raise RuntimeError("Can't switch container. See log for details.")

    if not hasattr(Loader, "switch"):
        # Backwards compatibility (classes without switch support
        # might be better to just have "switch" raise NotImplementedError
        # on the base class of Loader\
        raise RuntimeError("Loader '{}' does not support 'switch'".format(
            Loader.label
        ))

    # Get the new representation to switch to
    new_representation = io.find_one({
        "type": "representation",
        "_id": representation["_id"],
    })

    new_context = get_representation_context(new_representation)
    assert is_compatible_loader(Loader, new_context), ("Must be compatible "
                                                       "Loader")

    Loader = _make_backwards_compatible_loader(Loader)
    loader = Loader(new_context)

    return loader.switch(container, new_representation)


def get_representation_path(representation):
    """Get filename from representation document

    There are three ways of getting the path from representation which are
    tried in following sequence until successful.
    1. Get template from representation['data']['template'] and data from
       representation['context']. Then format template with the data.
    2. Get template from project['config'] and format it with default data set
    3. Get representation['data']['path'] and use it directly

    Args:
        representation(dict): representation document from the database

    Returns:
        str: fullpath of the representation

    """

    def path_from_represenation():
        try:
            template = representation["data"]["template"]

        except KeyError:
            return None

        try:
            context = representation["context"]
            context["root"] = registered_root()
            path = template.format(**context)

        except KeyError:
            # Template references unavailable data
            return None

        if os.path.exists(path):
            return os.path.normpath(path)

    def path_from_config():
        try:
            version_, subset, asset, project = io.parenthood(representation)
        except ValueError:
            log.debug(
                "Representation %s wasn't found in database, "
                "like a bug" % representation["name"]
            )
            return None

        try:
            template = project["config"]["template"]["publish"]
        except KeyError:
            log.debug(
                "No template in project %s, "
                "likely a bug" % project["name"]
            )
            return None

        # Cannot fail, required members only
        data = {
            "root": registered_root(),
            "project": project["name"],
            "asset": asset["name"],
            "silo": asset["silo"],
            "subset": subset["name"],
            "version": version_["name"],
            "representation": representation["name"],
            "user": Session.get("AVALON_USER", getpass.getuser()),
            "app": Session.get("AVALON_APP", ""),
            "task": Session.get("AVALON_TASK", "")
        }

        try:
            path = template.format(**data)
        except KeyError as e:
            log.debug("Template references unavailable data: %s" % e)
            return None

        if os.path.exists(path):
            return os.path.normpath(path)

    def path_from_data():
        if "path" not in representation["data"]:
            return None

        path = representation["data"]["path"]
        if os.path.exists(path):
            return os.path.normpath(path)

    return (
        path_from_represenation() or
        path_from_config() or
        path_from_data()
    )


def is_compatible_loader(Loader, context):
    """Return whether a loader is compatible with a context.

    This checks the version's families and the representation for the given
    Loader.

    Returns:
        bool

    """
    if context["subset"]["schema"] == "avalon-core:subset-3.0":
        families = context["subset"]["data"]["families"]
    else:
        families = context["version"]["data"].get("families", [])

    representation = context["representation"]
    has_family = ("*" in Loader.families or
                  any(family in Loader.families for family in families))
    has_representation = ("*" in Loader.representations or
                          representation["name"] in Loader.representations)
    return has_family and has_representation


def loaders_from_representation(loaders, representation):
    """Return all compatible loaders for a representation."""

    context = get_representation_context(representation)
    return [l for l in loaders if is_compatible_loader(l, context)]
