import os
import sys
import errno
import importlib
import contextlib

from maya import cmds, OpenMaya
from pyblish import api as pyblish

from . import lib, compat
from ..lib import logger
from .. import api, io, schema
from ..vendor import six
from ..vendor.Qt import QtCore, QtWidgets

self = sys.modules[__name__]
self._menu = "avalonmaya"  # Unique name of menu
self._events = dict()  # Registered Maya callbacks
self._parent = None  # Main Window
self._ignore_lock = False

IS_HEADLESS = not hasattr(cmds, "about") or cmds.about(batch=True)


def install(config):
    """Install Maya-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(maya)`.

    """

    # Inherit globally set name
    self._menu = api.Session["AVALON_LABEL"] + "menu"

    _register_callbacks()
    _set_project()

    # Check if maya version is compatible else fix it, Maya2018 only
    # Should be run regardless of batch mode
    if hasattr(cmds, "about") and cmds.about(version=True) == "2018":
        compat.install()

    if not IS_HEADLESS:
        _install_menu()

    pyblish.register_host("mayabatch")
    pyblish.register_host("mayapy")
    pyblish.register_host("maya")

    try:
        config = importlib.import_module(config.__name__ + ".maya")
    except ImportError:
        pass
    else:
        config.install()


def _set_project():
    workdir = os.environ["AVALON_WORKDIR"]

    try:
        os.makedirs(workdir)
    except OSError as e:
        # An already existing working directory is fine.
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

    cmds.workspace(workdir, openWorkspace=True)


def uninstall():
    _uninstall_menu()

    pyblish.deregister_host("mayabatch")
    pyblish.deregister_host("mayapy")
    pyblish.deregister_host("maya")


def _install_menu():
    from ..tools import (
        creator,
        loader,
        publish,
        cbloader,
        cbsceneinventory
    )

    from . import interactive

    _uninstall_menu()

    def deferred():
        cmds.menu(self._menu,
                  label=api.Session["AVALON_LABEL"],
                  tearOff=True,
                  parent="MayaWindow")

        cmds.menuItem("Create...",
                      command=lambda *args: creator.show(parent=self._parent))

        if api.Session.get("AVALON_EARLY_ADOPTER"):
            cmds.menuItem("Load...",
                          command=lambda *args:
                          cbloader.show(parent=self._parent))
        else:
            cmds.menuItem("Load...",
                          command=lambda *args:
                          loader.show(parent=self._parent))

        cmds.menuItem("Publish...",
                      command=lambda *args: publish.show(parent=self._parent),
                      image=publish.ICON)

        cmds.menuItem("Manage...",
                      command=lambda *args: cbsceneinventory.show(
                          parent=self._parent))

        cmds.menuItem(divider=True)

        cmds.menuItem("System",
                      label="System",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Reload Pipeline", command=reload_pipeline)

        cmds.setParent("..", menu=True)

        cmds.menuItem("Reset Frame Range",
                      command=interactive.reset_frame_range)
        cmds.menuItem("Reset Resolution",
                      command=interactive.reset_resolution)

    # Allow time for uninstallation to finish.
    QtCore.QTimer.singleShot(100, deferred)


def reload_pipeline(*args):
    """Attempt to reload pipeline at run-time.

    CAUTION: This is primarily for development and debugging purposes.

    """

    import importlib

    api.uninstall()

    for module in ("avalon.io",
                   "avalon.lib",
                   "avalon.pipeline",
                   "avalon.maya.commands",
                   "avalon.maya.interactive",
                   "avalon.maya.pipeline",
                   "avalon.maya.lib",
                   "avalon.tools.loader.app",
                   "avalon.tools.creator.app",
                   "avalon.tools.manager.app",

                   # NOTE(marcus): These have circular depenendencies
                   #               that is preventing reloadability
                   # "avalon.tools.cbloader.delegates",
                   # "avalon.tools.cbloader.lib",
                   # "avalon.tools.cbloader.model",
                   # "avalon.tools.cbloader.widgets",
                   # "avalon.tools.cbloader.app",
                   # "avalon.tools.cbsceneinventory.model",
                   # "avalon.tools.cbsceneinventory.proxy",
                   # "avalon.tools.cbsceneinventory.app",
                   # "avalon.tools.projectmanager.dialogs",
                   # "avalon.tools.projectmanager.lib",
                   # "avalon.tools.projectmanager.model",
                   # "avalon.tools.projectmanager.style",
                   # "avalon.tools.projectmanager.widget",
                   # "avalon.tools.projectmanager.app",

                   "avalon.api",
                   "avalon.tools",
                   "avalon.maya"):
        module = importlib.import_module(module)
        reload(module)

    self._parent = {
        widget.objectName(): widget
        for widget in QtWidgets.QApplication.topLevelWidgets()
    }["MayaWindow"]

    import avalon.maya
    api.install(avalon.maya)


def _uninstall_menu():
    app = QtWidgets.QApplication.instance()
    widgets = dict((w.objectName(), w) for w in app.allWidgets())
    menu = widgets.get(self._menu)

    if menu:
        menu.deleteLater()
        del(menu)


def lock():
    """Lock scene

    Add an invisible node to your Maya scene with the name of the
    current file, indicating that this file is "locked" and cannot
    be modified any further.

    """

    if not cmds.objExists("lock"):
        with lib.maintained_selection():
            cmds.createNode("objectSet", name="lock")
            cmds.addAttr("lock", ln="basename", dataType="string")

            # Permanently hide from outliner
            cmds.setAttr("lock.verticesOnlySet", True)

    fname = cmds.file(query=True, sceneName=True)
    basename = os.path.basename(fname)
    cmds.setAttr("lock.basename", basename, type="string")


def unlock():
    """Permanently unlock a locked scene

    Doesn't throw an error if scene is already unlocked.

    """

    try:
        cmds.delete("lock")
    except ValueError:
        pass


def is_locked():
    """Query whether current scene is locked"""
    fname = cmds.file(query=True, sceneName=True)
    basename = os.path.basename(fname)

    if self._ignore_lock:
        return False

    try:
        return cmds.getAttr("lock.basename") == basename
    except ValueError:
        return False


@contextlib.contextmanager
def lock_ignored():
    """Context manager for temporarily ignoring the lock of a scene

    The purpose of this function is to enable locking a scene and
    saving it with the lock still in place.

    Example:
        >>> with lock_ignored():
        ...   pass  # Do things without lock

    """

    self._ignore_lock = True

    try:
        yield
    finally:
        self._ignore_lock = False


def containerise(name,
                 namespace,
                 nodes,
                 context,
                 loader=None,
                 suffix="_CON"):
    """Bundle `nodes` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        nodes (list): Long names of nodes to containerise
        context (dict): Asset information
        loader (str, optional): Name of loader used to produce this container.
        suffix (str, optional): Suffix of container, defaults to `_CON`.

    Returns:
        container (str): Name of container assembly

    """

    container = cmds.sets(nodes, name="%s_%s_%s" % (namespace, name, suffix))

    data = [
        ("schema", "avalon-core:container-2.0"),
        ("id", "pyblish.avalon.container"),
        ("name", name),
        ("namespace", namespace),
        ("loader", str(loader)),
        ("representation", context["representation"]["_id"]),
    ]

    for key, value in data:
        if not value:
            continue

        if isinstance(value, (int, float)):
            cmds.addAttr(container, longName=key, attributeType="short")
            cmds.setAttr(container + "." + key, value)

        else:
            cmds.addAttr(container, longName=key, dataType="string")
            cmds.setAttr(container + "." + key, value, type="string")

    # Hide in outliner
    cmds.setAttr(container + ".verticesOnlySet", True)

    return container


def ls():
    """List containers from active Maya scene

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Maya; once loaded
    they are called 'containers'

    """

    containers = list()
    for identifier in ("pyblish.avalon.container",
                       "pyblish.mindbender.container"):
        containers += lib.lsattr("id", identifier)

    for container in sorted(containers):
        data = lib.read(container)

        # Backwards compatibility pre-schemas for containers
        data["schema"] = data.get("schema", "avalon-core:container-1.0")

        # Append transient data
        data["objectName"] = container

        schema.validate(data)

        yield data


def load(Loader,
         representation,
         name=None,
         namespace=None,
         data=None):
    """Load asset via database

    Arguments:
        Loader (api.Loader): The loader to process in host Maya.
        representation (dict, io.ObjectId or str): Address to representation
        name (str, optional): Use pre-defined name
        namespace (str, optional): Use pre-defined namespace
        data (dict, optional): Additional settings dictionary

    """

    assert representation is not None, "This is a bug"

    if isinstance(representation, (six.string_types, io.ObjectId)):
        representation = io.find_one({"_id": io.ObjectId(str(representation))})

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

    # Ensure data is a dictionary when no explicit data provided
    if data is None:
        data = dict()
    assert isinstance(data, dict), "Data must be a dictionary"

    name = name or subset["name"]
    namespace = namespace or lib.unique_namespace(
        asset["name"] + "_",
        prefix="_" if asset["name"][0].isdigit() else "",
        suffix="_",
    )

    # TODO(roy): add compatibility check, see `tools.cbloader.lib`

    Loader.log.info(
        "Running '%s' on '%s'" % (Loader.__name__, asset["name"])
    )

    try:
        loader = Loader(context)

        with lib.maintained_selection():
            loader.process(name, namespace, context, data)

    except OSError as e:
        logger.info("WARNING: %s" % e)
        return list()

    return containerise(
        name=name,
        namespace=namespace,
        nodes=loader[:],
        context=context,
        loader=Loader.__name__)


class Creator(api.Creator):
    def process(self):
        nodes = list()

        if (self.options or {}).get("useSelection"):
            nodes = cmds.ls(selection=True)

        instance = cmds.sets(nodes, name=self.name)
        lib.imprint(instance, self.data)

        return instance


class Loader(api.Loader):
    def __init__(self, context):
        super(Loader, self).__init__(context)
        self.fname = self.fname.replace(
            api.registered_root(), "$AVALON_PROJECTS"
        )


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

    plugins = list()
    for Plugin in api.discover(api.Creator):
        has_family = family == Plugin.family

        if not has_family:
            continue

        Plugin.log.info(
            "Creating '%s' with '%s'" % (name, Plugin.__name__)
        )

        try:
            plugin = Plugin(name, asset, options, data)

            with lib.maintained_selection():
                instance = plugin.process()
        except Exception as e:
            logger.info("WARNING: %s" % e)
            continue

        plugins.append(plugin)

    assert plugins, "No Creator plug-ins were run, this is a bug"
    return instance


def update(container, version=-1):
    """Update `container` to `version`

    This function relies on a container being referenced. At the time of this
    writing, all assets - models, rigs, animations, shaders - are referenced
    and should pose no problem. But should there be an asset that isn't
    referenced then this function will need to see an update.

    Arguments:
        container (avalon-core:container-1.0): Container to update,
            from `host.ls()`.
        version (int, optional): Update the container to this version.
            If no version is passed, the latest is assumed.

    """

    node = container["objectName"]

    # Assume asset has been referenced
    reference_node = next((node for node in cmds.sets(node, query=True)
                          if cmds.nodeType(node) == "reference"), None)

    assert reference_node, ("Imported container not supported; "
                            "container must be referenced.")

    current_representation = io.find_one({
        "_id": io.ObjectId(container["representation"])
    })

    assert current_representation is not None, "This is a bug"

    version_, subset, asset, project = io.parenthood(current_representation)

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

    template_publish = project["config"]["template"]["publish"]
    fname = template_publish.format(**{
        "root": api.registered_root(),
        "project": project["name"],
        "asset": asset["name"],
        "silo": asset["silo"],
        "subset": subset["name"],
        "version": new_version["name"],
        "representation": current_representation["name"],
    })

    file_type = {
        "ma": "mayaAscii",
        "mb": "mayaBinary",
        "abc": "Alembic"
    }.get(new_representation["name"])

    assert file_type, ("Unsupported representation: %s" % new_representation)

    assert os.path.exists(fname), "%s does not exist." % fname
    cmds.file(fname, loadReference=reference_node, type=file_type)

    # Update metadata
    cmds.setAttr(container["objectName"] + ".representation",
                 str(new_representation["_id"]),
                 type="string")


def remove(container):
    """Remove an existing `container` from Maya scene

    Arguments:
        container (avalon-core:container-1.0): Which container
            to remove from scene.

    """

    node = container["objectName"]

    # Assume asset has been referenced
    reference_node = next((node for node in cmds.sets(node, query=True)
                          if cmds.nodeType(node) == "reference"), None)

    assert reference_node, ("Imported container not supported; "
                            "container must be referenced.")

    logger.info("Removing '%s' from Maya.." % container["name"])

    namespace = cmds.referenceQuery(reference_node, namespace=True)
    fname = cmds.referenceQuery(reference_node, filename=True)
    cmds.file(fname, removeReference=True)

    try:
        cmds.delete(node)
    except ValueError:
        # Already implicitly deleted by Maya upon removing reference
        pass

    try:
        # If container is not automatically cleaned up by May (issue #118)
        cmds.namespace(removeNamespace=namespace, deleteNamespaceContent=True)
    except RuntimeError:
        pass


def publish():
    """Shorthand to publish from within host"""
    import pyblish.util
    return pyblish.util.publish()


def _register_callbacks():
    for handler, event in self._events.copy().items():
        if event is None:
            continue

        try:
            OpenMaya.MMessage.removeCallback(event)
            self._events[handler] = None
        except RuntimeError as e:
            logger.info(e)

    self._events[_on_scene_save] = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kBeforeSave, _on_scene_save
    )

    self._events[_before_scene_save] = OpenMaya.MSceneMessage.addCheckCallback(
        OpenMaya.MSceneMessage.kBeforeSaveCheck, _before_scene_save
    )

    self._events[_on_scene_new] = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kAfterNew, _on_scene_new
    )

    self._events[_on_maya_initialized] = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kMayaInitialized, _on_maya_initialized
    )

    logger.info("Installed event handler _on_scene_save..")
    logger.info("Installed event handler _before_scene_save..")
    logger.info("Installed event handler _on_scene_new..")
    logger.info("Installed event handler _on_maya_initialized..")


def _on_maya_initialized(*args):
    api.emit("init", args)

    # Keep reference to the main Window, once a main window exists.
    self._parent = {
        widget.objectName(): widget
        for widget in QtWidgets.QApplication.topLevelWidgets()
    }["MayaWindow"]


def _on_scene_new(*args):
    api.emit("new", args)


def _on_scene_save(*args):
    api.emit("save", args)


def _before_scene_save(return_code, client_data):

    # Default to allowing the action. Registered
    # callbacks can optionally set this to False
    # in order to block the operation.
    OpenMaya.MScriptUtil.setBool(return_code, True)

    api.emit("before_save", [return_code, client_data])
