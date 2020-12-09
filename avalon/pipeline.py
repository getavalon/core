"""Core pipeline functionality"""

import os
import sys
import re
import json
import errno
import types
import copy
import shutil
import getpass
import logging
import weakref
import inspect
import traceback
import platform
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
if os.environ.get("PYPE_ROOT"):
    from pype.api import Anatomy
else:
    Anatomy = None

self = sys.modules[__name__]
self._is_installed = False
self._config = None
self.data = {}

log = logging.getLogger(__name__)


AVALON_CONTAINER_ID = "pyblish.avalon.container"

HOST_WORKFILE_EXTENSIONS = {
    "blender": [".blend"],
    "celaction": [".scn"],
    "tvpaint": [".tvpp"],
    "fusion": [".comp"],
    "harmony": [".zip"],
    "houdini": [".hip", ".hiplc", ".hipnc"],
    "maya": [".ma", ".mb"],
    "nuke": [".nk"],
    "hiero": [".hrox"],
    "photoshop": [".psd"],
    "premiere": [".prproj"],
    "resolve": [".drp"],
    "aftereffects": [".aep"]
}


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
        host.install()

    # Optional config.host.install()
    host_name = host.__name__.rsplit(".", 1)[-1]
    config_host = lib.find_submodule(config, host_name)
    if config_host != host:
        if hasattr(config_host, "install"):
            config_host.install()

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
    host = registered_host()

    # Optional config.host.uninstall()
    host_name = host.__name__.rsplit(".", 1)[-1]
    config_host = lib.find_submodule(config, host_name)
    if hasattr(config_host, "uninstall"):
        config_host.uninstall()

    try:
        host.uninstall()
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
        self.fname = self.filepath_from_context(context)

    def filepath_from_context(self, context):
        """Fill representation path from entered context."""
        representation = context["representation"]
        root = None
        if Anatomy:
            project_doc = context.get("project")
            session_project = Session.get("AVALON_PROJECT")
            # Check if project name of context is same as global session
            if project_doc and project_doc["name"] != session_project:
                # If they're not same load roots of the project
                anatomy = Anatomy(project_doc["name"])
                root = anatomy.roots_obj

        return get_representation_path(representation, root)

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


class CreatorError(Exception):
    """Should be raised when creator failed because of known issue.

    Message of error should be user readable.
    """

    def __init__(self, message):
        super(CreatorError, self).__init__(message)


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


@lib.log
class ThumbnailResolver(object):
    """Determine how to get data from thumbnail entity.

    "priority" - determines the order of processing in `get_thumbnail_binary`,
        lower number is processed earlier.
    "thumbnail_types" - it is expected that thumbnails will be used in more
        more than one level, there is only ["thumbnail"] type at the moment
        of creating this docstring but it is expected to add "ico" and "full"
        in future.
    """

    priority = 100
    thumbnail_types = ["*"]

    def __init__(self, dbcon):
        self.dbcon = dbcon

    def process(self, thumbnail_entity, thumbnail_type):
        pass


class TemplateResolver(ThumbnailResolver):

    priority = 90

    def process(self, thumbnail_entity, thumbnail_type):

        if not os.environ.get("AVALON_THUMBNAIL_ROOT"):
            return

        template = thumbnail_entity["data"].get("template")
        if not template:
            log.debug("Thumbnail entity does not have set template")
            return

        project = self.dbcon.find_one({"type": "project"})

        template_data = copy.deepcopy(
            thumbnail_entity["data"].get("template_data") or {}
        )
        template_data.update({
            "_id": str(thumbnail_entity["_id"]),
            "thumbnail_type": thumbnail_type,
            "thumbnail_root": os.environ.get("AVALON_THUMBNAIL_ROOT"),
            "project": {
                "name": project["name"],
                "code": project["data"].get("code")
            }
        })

        try:
            filepath = os.path.normpath(template.format(**template_data))
        except KeyError:
            log.warning((
                "Missing template data keys for template <{0}> || Data: {1}"
            ).format(template, str(template_data)))
            return

        if not os.path.exists(filepath):
            log.warning("File does not exist \"{0}\"".format(filepath))
            return

        with open(filepath, "rb") as _file:
            content = _file.read()

        return content


class BinaryThumbnail(ThumbnailResolver):

    def process(self, thumbnail_entity, thumbnail_type):
        return thumbnail_entity["data"].get("binary_data")


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


register_plugin(ThumbnailResolver, BinaryThumbnail)
register_plugin(ThumbnailResolver, TemplateResolver)


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
    root = _registered_root["_"]
    if root:
        return root

    root = Session.get("AVALON_PROJECTS")
    if root:
        return os.path.normpath(root)

    return ""


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
            if sys.version_info.major >= 3:
                signature = inspect.getfullargspec(attr)[0]
            else:
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


def create(Creator, name, asset, options=None, data=None):
    """Create a new instance

    Associate nodes with a subset and family. These nodes are later
    validated, according to their `family`, and integrated into the
    shared environment, relative their `subset`.

    Data relative each family, along with default data, are imprinted
    into the resulting objectSet. This data is later used by extractors
    and finally asset browsers to help identify the origin of the asset.

    Arguments:
        Creator (Creator): Class of creator
        name (str): Name of subset
        asset (str): Name of asset
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
    plugin = Creator(name, asset, options, data)
    with host.maintained_selection():
        print("Running %s" % plugin)
        instance = plugin.process()

    return instance


def get_repres_contexts(representation_ids, dbcon=None):
    """Return parenthood context for representation.

    Args:
        representation_ids (list): The representation ids.
        dbcon (AvalonMongoDB): Mongo connection object. `avalon.io` used when
            not entered.

    Returns:
        dict: The full representation context by representation id.

    """
    if not dbcon:
        dbcon = io

    contexts = {}
    if not representation_ids:
        return contexts

    _representation_ids = []
    for repre_id in representation_ids:
        if isinstance(repre_id, six.string_types):
            repre_id = io.ObjectId(repre_id)
        _representation_ids.append(repre_id)

    repre_docs = dbcon.find({
        "type": "representation",
        "_id": {"$in": _representation_ids}
    })
    repre_docs_by_id = {}
    version_ids = set()
    for repre_doc in repre_docs:
        version_ids.add(repre_doc["parent"])
        repre_docs_by_id[repre_doc["_id"]] = repre_doc

    version_docs = dbcon.find({
        "type": "version",
        "_id": {"$in": list(version_ids)}
    })
    version_docs_by_id = {}
    subset_ids = set()
    for version_doc in version_docs:
        version_docs_by_id[version_doc["_id"]] = version_doc
        subset_ids.add(version_doc["parent"])

    subset_docs = dbcon.find({
        "type": "subset",
        "_id": {"$in": list(subset_ids)}
    })
    subset_docs_by_id = {}
    asset_ids = set()
    for subset_doc in subset_docs:
        subset_docs_by_id[subset_doc["_id"]] = subset_doc
        asset_ids.add(subset_doc["parent"])

    asset_docs = dbcon.find({
        "type": "asset",
        "_id": {"$in": list(asset_ids)}
    })
    asset_docs_by_id = {
        asset_doc["_id"]: asset_doc
        for asset_doc in asset_docs
    }

    project_doc = dbcon.find_one({"type": "project"})

    for repre_id, repre_doc in repre_docs_by_id.items():
        version_doc = version_docs_by_id[repre_doc["parent"]]
        subset_doc = subset_docs_by_id[version_doc["parent"]]
        asset_doc = asset_docs_by_id[subset_doc["parent"]]
        context = {
            "project": {
                "name": project_doc["name"],
                "code": project_doc["data"].get("code")
            },
            "asset": asset_doc,
            "subset": subset_doc,
            "version": version_doc,
            "representation": repre_doc,
        }
        contexts[repre_id] = context

    return contexts


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
        "project": {
            "name": project["name"],
            "code": project["data"].get("code", '')
        },
        "asset": asset,
        "subset": subset,
        "version": version,
        "representation": representation,
    }

    return context


def template_data_from_session(session):
    """ Return dictionary with template from session keys.

    Args:
        session (dict, Optional): The Session to use. If not provided use the
            currently active global Session.
    Returns:
        dict: All available data from session.
    """
    if session is None:
        session = Session

    project_name = session["AVALON_PROJECT"]
    project_doc = io._database[project_name].find_one(
        {"type": "project"}
    )
    asset_doc = io._database[project_name].find_one(
        {
            "type": "asset",
            "name": session["AVALON_ASSET"]
        },
        {
            "data.parents": True
        }
    )
    asset_parents = asset_doc["data"].get("parents") or []
    hierarchy = "/".join(asset_parents)

    return {
        "root": registered_root(),
        "project": {
            "name": project_doc.get("name", project_name),
            "code": project_doc["data"].get("code") or "",
        },
        "asset": session["AVALON_ASSET"],
        "task": session["AVALON_TASK"],
        "app": session["AVALON_APP"],

        # Optional
        "silo": session.get("AVALON_SILO"),
        "user": session.get("AVALON_USER", getpass.getuser()),
        "hierarchy": hierarchy
    }


def compute_session_changes(session, task=None, asset=None, app=None):
    """Compute the changes for a Session object on asset, task or app switch

    This does *NOT* update the Session object, but returns the changes
    required for a valid update of the Session.

    Args:
        session (dict): The initial session to compute changes to.
            This is required for computing the full Work Directory, as that
            also depends on the values that haven't changed.
        task (str, Optional): Name of task to switch to.
        asset (str or dict, Optional): Name of asset to switch to.
            You can also directly provide the Asset dictionary as returned
            from the database to avoid an additional query. (optimization)
        app (str, Optional): Name of app to switch to.

    Returns:
        dict: The required changes in the Session dictionary.

    """

    changes = dict()

    # If no changes, return directly
    if not any([task, asset, app]):
        return changes

    # Get asset document and asset
    asset_document = None
    if asset:
        if isinstance(asset, dict):
            # Assume asset database document
            asset_document = asset
            asset = asset["name"]
        else:
            # Assume asset name
            asset_document = io.find_one({"name": asset,
                                          "type": "asset"})
            assert asset_document, "Asset must exist"

    # Detect any changes compared session
    mapping = {
        "AVALON_ASSET": asset,
        "AVALON_TASK": task,
        "AVALON_APP": app,
    }
    changes = {key: value for key, value in mapping.items()
               if value and value != session.get(key)}
    if not changes:
        return changes

    # Update silo and hierarchy when asset changed
    if "AVALON_ASSET" in changes:

        # Update silo
        changes["AVALON_SILO"] = asset_document.get("silo") or ""

    # Compute work directory (with the temporary changed session so far)
    _session = session.copy()
    _session.update(changes)

    if Anatomy:
        anatomy = Anatomy(io.Session["AVALON_PROJECT"])
        template_data = template_data_from_session(_session)
        anatomy_filled = anatomy.format(template_data)
        workdir = anatomy_filled["work"]["folder"]
    else:
        project_doc = io.find_one(
            {"type": "project"},
            projection={"config.template.work": True}
        )
        template = project_doc["config"]["template"]["work"]
        workdir = _format_work_template(template, _session)

    changes["AVALON_WORKDIR"] = workdir

    return changes


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

    changes = compute_session_changes(
        Session, task=task, asset=asset, app=app
    )

    # Update the Session and environments. Pop from environments all keys with
    # value set to None.
    for key, value in changes.items():
        Session[key] = value
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    # Emit session change
    emit("taskChanged", changes.copy())

    return changes


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

    fill_data = template_data_from_session(session)

    return template.format(**fill_data)


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


def load_with_repre_context(
    Loader, repre_context, namespace=None, name=None, options=None, **kwargs
):
    Loader = _make_backwards_compatible_loader(Loader)

    # Ensure the Loader is compatible for the representation
    if not is_compatible_loader(Loader, repre_context):
        raise IncompatibleLoaderError(
            "Loader {} is incompatible with {}".format(
                Loader.__name__, repre_context["subset"]["name"]
            )
        )

    # Ensure options is a dictionary when no explicit options provided
    if options is None:
        options = kwargs.get("data", dict())  # "data" for backward compat

    assert isinstance(options, dict), "Options must be a dictionary"

    # Fallback to subset when name is None
    if name is None:
        name = repre_context["subset"]["name"]

    log.info(
        "Running '%s' on '%s'" % (
            Loader.__name__, repre_context["asset"]["name"]
        )
    )

    loader = Loader(repre_context)
    return loader.load(repre_context, name, namespace, options)


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

    context = get_representation_context(representation)
    return load_with_repre_context(
        Loader,
        context,
        namespace=namespace,
        name=name,
        options=options,
        **kwargs
    )


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
        if isinstance(version, lib.MasterVersionType):
            version_query = {
                "parent": subset["_id"],
                "type": "master_version"
            }
        else:
            version_query = {
                "parent": subset["_id"],
                "type": "version",
                "name": version
            }
        new_version = io.find_one(version_query)

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


def format_template_with_optional_keys(data, template):
    # Remove optional missing keys
    pattern = re.compile(r"(<.*?[^{0]*>)[^0-9]*?")
    invalid_optionals = []
    for group in pattern.findall(template):
        try:
            group.format(**data)
        except KeyError:
            invalid_optionals.append(group)

    for group in invalid_optionals:
        template = template.replace(group, "")

    work_file = template.format(**data)

    # Remove optional symbols
    work_file = work_file.replace("<", "")
    work_file = work_file.replace(">", "")

    # Remove double dots when dot for extension is in template
    work_file = work_file.replace("..", ".")

    return work_file


def get_representation_path(representation, root=None, dbcon=None):
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
    if dbcon is None:
        dbcon = io

    if root is None:
        root = registered_root()

    def path_from_represenation():
        try:
            template = representation["data"]["template"]
        except KeyError:
            return None

        try:
            context = representation["context"]
            context["root"] = root
            path = format_template_with_optional_keys(context, template)
        except KeyError:
            # Template references unavailable data
            return None

        if not path:
            return path

        normalized_path = os.path.normpath(path)
        if os.path.exists(normalized_path):
            return normalized_path
        return path

    def path_from_config():
        try:
            version_, subset, asset, project = dbcon.parenthood(representation)
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

        # hierarchy may be equal to "" so it is not possible to use `or`
        hierarchy = asset.get("data", {}).get("hierarchy")
        if hierarchy is None:
            # default list() in get would not discover missing parents on asset
            parents = asset.get("data", {}).get("parents")
            if parents is not None:
                hierarchy = "/".join(parents)

        # Cannot fail, required members only
        data = {
            "root": root,
            "project": {
                "name": project["name"],
                "code": project.get("data", {}).get("code")
            },
            "asset": asset["name"],
            "silo": asset.get("silo"),
            "hierarchy": hierarchy,
            "subset": subset["name"],
            "version": version_["name"],
            "representation": representation["name"],
            "family": representation.get("context", {}).get("family"),
            "user": dbcon.Session.get("AVALON_USER", getpass.getuser()),
            "app": dbcon.Session.get("AVALON_APP", ""),
            "task": dbcon.Session.get("AVALON_TASK", "")
        }

        try:
            path = format_template_with_optional_keys(data, template)
        except KeyError as e:
            log.debug("Template references unavailable data: %s" % e)
            return None

        normalized_path = os.path.normpath(path)
        if os.path.exists(normalized_path):
            return normalized_path
        return path

    def path_from_data():
        if "path" not in representation["data"]:
            return None

        path = representation["data"]["path"]
        if os.path.exists(path):
            return os.path.normpath(path)

        dir_path, file_name = os.path.split(path)
        if not os.path.exists(dir_path):
            return

        base_name, ext = os.path.splitext(file_name)
        file_name_items = None
        if "#" in base_name:
            file_name_items = [part for part in base_name.split("#") if part]
        elif "%" in base_name:
            file_name_items = base_name.split("%")

        if not file_name_items:
            return

        filename_start = file_name_items[0]

        for _file in os.listdir(dir_path):
            if _file.startswith(filename_start) and _file.endswith(ext):
                return os.path.normpath(path)

    return (
        path_from_represenation() or
        path_from_config() or
        path_from_data()
    )


def get_thumbnail_binary(thumbnail_entity, thumbnail_type, dbcon=None):
    if not thumbnail_entity:
        return

    resolvers = discover(ThumbnailResolver)
    resolvers = sorted(resolvers, key=lambda cls: cls.priority)
    if dbcon is None:
        dbcon = io

    for Resolver in resolvers:
        available_types = Resolver.thumbnail_types
        if (
            thumbnail_type not in available_types
            and "*" not in available_types
            and (
                isinstance(available_types, (list, tuple))
                and len(available_types) == 0
            )
        ):
            continue
        try:
            instance = Resolver(dbcon)
            result = instance.process(thumbnail_entity, thumbnail_type)
            if result:
                return result

        except Exception:
            log.warning("Resolver {0} failed durring process.".format(
                Resolver.__class__.__name__
            ))
            traceback.print_exception(*sys.exc_info())


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


def loaders_from_repre_context(loaders, repre_context):
    """Return compatible loaders for by representaiton's context."""

    return [
        loader
        for loader in loaders
        if is_compatible_loader(loader, repre_context)
    ]


def loaders_from_representation(loaders, representation):
    """Return all compatible loaders for a representation."""

    context = get_representation_context(representation)
    return loaders_from_repre_context(loaders, context)


def last_workfile_with_version(workdir, file_template, fill_data, extensions):
    """Return last workfile version.

    Args:
        workdir(str): Path to dir where workfiles are stored.
        file_template(str): Template of file name.
        fill_data(dict): Data for filling template.
        extensions(list, tuple): All allowed file extensions of workfile.

    Returns:
        tuple: Last workfile<str> with version<int> if there is any otherwise
            returns (None, None).
    """
    if not os.path.exists(workdir):
        return None, None

    # Fast match on extension
    filenames = [
        filename
        for filename in os.listdir(workdir)
        if os.path.splitext(filename)[1] in extensions
    ]

    # Build template without optionals, version to digits only regex
    # and comment to any definable value.
    _ext = []
    for ext in extensions:
        if not ext.startswith("."):
            ext = "." + ext
        # Escape dot for regex
        ext = "\\" + ext
        _ext.append(ext)
    ext_expression = "(?:" + "|".join(_ext) + ")"

    # Replace `.{ext}` with `{ext}` so we are sure there is not dot at the end
    file_template = re.sub(r"\.?{ext}", ext_expression, file_template)
    # Replace optional keys with optional content regex
    file_template = re.sub(r"<.*?>", r".*?", file_template)
    # Replace `{version}` with group regex
    file_template = re.sub(r"{version.*?}", r"([0-9]+)", file_template)
    file_template = re.sub(r"{comment.*?}", r".+?", file_template)
    file_template = format_template_with_optional_keys(
        fill_data,
        file_template
    )

    # Match with ignore case on Windows due to the Windows
    # OS not being case-sensitive. This avoids later running
    # into the error that the file did exist if it existed
    # with a different upper/lower-case.
    kwargs = {}
    if platform.system().lower() == "windows":
        kwargs["flags"] = re.IGNORECASE

    # Get highest version among existing matching files
    version = None
    output_filenames = []
    for filename in sorted(filenames):
        match = re.match(file_template, filename, **kwargs)
        if not match:
            continue

        file_version = int(match.group(1))
        if version is None or file_version > version:
            output_filenames[:] = []
            version = file_version

        if file_version == version:
            output_filenames.append(filename)

    output_filename = None
    if output_filenames:
        if len(output_filenames) == 1:
            output_filename = output_filenames[0]
        else:
            last_time = None
            for _output_filename in output_filenames:
                full_path = os.path.join(workdir, _output_filename)
                mod_time = os.path.getmtime(full_path)
                if last_time is None or last_time < mod_time:
                    output_filename = _output_filename
                    last_time = mod_time

    return output_filename, version


def last_workfile(
    workdir, file_template, fill_data, extensions, full_path=False
):
    """Return last workfile filename.

    Returns file with version 1 if there is not workfile yet.

    Args:
        workdir(str): Path to dir where workfiles are stored.
        file_template(str): Template of file name.
        fill_data(dict): Data for filling template.
        extensions(list, tuple): All allowed file extensions of workfile.
        full_path(bool): Full path to file is returned if set to True.

    Returns:
        str: Last or first workfile as filename of full path to filename.
    """
    filename, version = last_workfile_with_version(
        workdir, file_template, fill_data, extensions
    )
    if filename is None:
        data = copy.deepcopy(fill_data)
        data["version"] = 1
        data.pop("comment", None)
        if not data.get("ext"):
            data["ext"] = extensions[0]
        filename = format_template_with_optional_keys(data, file_template)

    if full_path:
        return os.path.join(workdir, filename)
    return filename
