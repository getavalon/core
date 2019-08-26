import os
import sys
import errno
import importlib
import contextlib

from maya import cmds, OpenMaya
from pyblish import api as pyblish

from . import lib, compat
from ..lib import logger
from .. import api, schema
from ..tools import workfiles
from ..vendor.Qt import QtCore, QtWidgets

from ..pipeline import AVALON_CONTAINER_ID

# Backwards compatibility
load = compat.load
update = compat.update
remove = compat.remove
create = compat.create

self = sys.modules[__name__]
self._menu = "avalonmaya"  # Unique name of menu
self._events = dict()  # Registered Maya callbacks
self._parent = None  # Main Window
self._ignore_lock = False

AVALON_CONTAINERS = ":AVALON_CONTAINERS"
IS_HEADLESS = not hasattr(cmds, "about") or cmds.about(batch=True)


def install(config):
    """Install Maya-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(maya)`.

    """

    # Inherit globally set name
    self._menu = api.Session["AVALON_LABEL"] + "menu"

    _register_callbacks()
    _register_events()
    _set_project()

    # Check if maya version is compatible else fix it, Maya2018 only
    # Should be run regardless of batch mode
    compat.install()

    if not IS_HEADLESS:
        _install_menu()

    pyblish.register_host("mayabatch")
    pyblish.register_host("mayapy")
    pyblish.register_host("maya")

    config = find_host_config(config)
    if hasattr(config, "install"):
        config.install()


def _set_project():
    """Sets the maya project to the current Session's work directory.

    Returns:
        None

    """
    workdir = api.Session["AVALON_WORKDIR"]

    try:
        os.makedirs(workdir)
    except OSError as e:
        # An already existing working directory is fine.
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

    cmds.workspace(workdir, openWorkspace=True)


def find_host_config(config):
    try:
        config = importlib.import_module(config.__name__ + ".maya")
    except ImportError as exc:
        if str(exc) != "No module name {}".format(config.__name__ + ".maya"):
            raise
        config = None

    return config


def uninstall(config):
    """Uninstall Maya-specific functionality of avalon-core.

    This function is called automatically on calling `api.uninstall()`.

    """
    config = find_host_config(config)
    if hasattr(config, "uninstall"):
        config.uninstall()

    _uninstall_menu()

    pyblish.deregister_host("mayabatch")
    pyblish.deregister_host("mayapy")
    pyblish.deregister_host("maya")


def _install_menu():
    from ..tools import (
        projectmanager,
        creator,
        loader,
        publish,
        sceneinventory,
        contextmanager
    )

    from . import interactive

    _uninstall_menu()

    def deferred():
        cmds.menu(self._menu,
                  label=api.Session["AVALON_LABEL"],
                  tearOff=True,
                  parent="MayaWindow")

        # Create context menu
        context_label = "{}, {}".format(api.Session["AVALON_ASSET"],
                                        api.Session["AVALON_TASK"])
        context_menu = cmds.menuItem("currentContext",
                                     label=context_label,
                                     parent=self._menu,
                                     subMenu=True)

        cmds.menuItem("setCurrentContext",
                      label="Edit Context..",
                      parent=context_menu,
                      command=lambda *args: contextmanager.show(
                          parent=self._parent
                      ))

        cmds.setParent("..", menu=True)

        cmds.menuItem(divider=True)

        # Create default items
        cmds.menuItem("Create...",
                      command=lambda *args: creator.show(parent=self._parent))

        cmds.menuItem("Load...",
                      command=lambda *args: loader.show(parent=self._parent,
                                                        use_context=True))

        cmds.menuItem("Publish...",
                      command=lambda *args: publish.show(parent=self._parent),
                      image=publish.ICON)

        cmds.menuItem("Manage...",
                      command=lambda *args: sceneinventory.show(
                          parent=self._parent))

        cmds.menuItem(divider=True)

        cmds.menuItem("Work Files", command=launch_workfiles_app)

        system = cmds.menuItem("System",
                               label="System",
                               tearOff=True,
                               subMenu=True,
                               parent=self._menu)

        cmds.menuItem("Project Manager",
                      command=lambda *args: projectmanager.show(
                        parent=self._parent))

        cmds.menuItem("Reinstall Avalon",
                      label="Reinstall Avalon",
                      subMenu=True,
                      parent=system)

        cmds.menuItem("Confirm", command=reload_pipeline)

        cmds.setParent(self._menu, menu=True)

        cmds.menuItem("Reset Frame Range",
                      command=interactive.reset_frame_range)
        cmds.menuItem("Reset Resolution",
                      command=interactive.reset_resolution)

    # Allow time for uninstallation to finish.
    QtCore.QTimer.singleShot(100, deferred)


def launch_workfiles_app(*args):
    workfiles.show(
        os.path.join(
            cmds.workspace(query=True, rootDirectory=True),
            cmds.workspace(fileRuleEntry="scene")
        )
    )


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
                   "avalon.tools.creator.app",

                   # NOTE(marcus): These have circular depenendencies
                   #               that is preventing reloadability
                   # "avalon.tools.loader.delegates",
                   # "avalon.tools.loader.model",
                   # "avalon.tools.loader.widgets",
                   # "avalon.tools.loader.app",
                   # "avalon.tools.sceneinventory.model",
                   # "avalon.tools.sceneinventory.proxy",
                   # "avalon.tools.sceneinventory.app",
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


def _update_menu_task_label():
    """Update the task label in Avalon menu to current session"""

    if IS_HEADLESS:
        return

    object_name = "{}|currentContext".format(self._menu)
    if not cmds.menuItem(object_name, query=True, exists=True):
        logger.warning("Can't find menuItem: {}".format(object_name))
        return

    label = "{}, {}".format(api.Session["AVALON_ASSET"],
                            api.Session["AVALON_TASK"])
    cmds.menuItem(object_name, edit=True, label=label)


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
                 suffix="CON"):
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
        ("id", AVALON_CONTAINER_ID),
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

    main_container = cmds.ls(AVALON_CONTAINERS, type="objectSet")
    if not main_container:
        main_container = cmds.sets(empty=True, name=AVALON_CONTAINERS)

        # Implement #399: Maya 2019+ hide AVALON_CONTAINERS on creation..
        if cmds.attributeQuery("hiddenInOutliner",
                               node=main_container,
                               exists=True):
            cmds.setAttr(main_container + ".hiddenInOutliner", True)
    else:
        main_container = main_container[0]

    cmds.sets(container, addElement=main_container)

    # Implement #399: Maya 2019+ hide containers in outliner
    if cmds.attributeQuery("hiddenInOutliner",
                           node=container,
                           exists=True):
        cmds.setAttr(container + ".hiddenInOutliner", True)

    return container


def parse_container(container, validate=True):
    """Return the container node's full container data.

    Args:
        container (str): A container node name.

    Returns:
        dict: The container schema data for this container node.

    """
    data = lib.read(container)

    # Backwards compatibility pre-schemas for containers
    data["schema"] = data.get("schema", "avalon-core:container-1.0")

    # Append transient data
    data["objectName"] = container

    if validate:
        schema.validate(data)

    return data


def _ls():
    containers = list()
    for identifier in (AVALON_CONTAINER_ID,
                       "pyblish.mindbender.container"):
        containers += lib.lsattr("id", identifier)

    return containers


def ls():
    """List containers from active Maya scene

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Maya; once loaded
    they are called 'containers'

    """
    container_names = _ls()

    has_metadata_collector = False
    config = find_host_config(api.registered_config())
    if hasattr(config, "collect_container_metadata"):
        has_metadata_collector = True

    for container in sorted(container_names):
        data = parse_container(container)

        # Collect custom data if attribute is present
        if has_metadata_collector:
            metadata = config.collect_container_metadata(container)
            data.update(metadata)

        yield data


def update_hierarchy(containers):
    """Hierarchical container support

    This is the function to support Scene Inventory to draw hierarchical
    view for containers.

    We need both parent and children to visualize the graph.

    """
    container_names = set(_ls())  # lookup set

    for container in containers:
        # Find parent
        parent = cmds.listSets(object=container["objectName"]) or []
        for node in parent:
            if node in container_names:
                container["parent"] = node
                break

        # List children
        children = cmds.ls(cmds.sets(container["objectName"], query=True),
                           type="objectSet")
        container["children"] = [child for child in children
                                 if child in container_names]

        yield container


class Creator(api.Creator):
    def process(self):
        nodes = list()

        with lib.undo_chunk():
            if (self.options or {}).get("useSelection"):
                nodes = cmds.ls(selection=True)

            instance = cmds.sets(nodes, name=self.name)
            lib.imprint(instance, self.data)

        return instance


class Loader(api.Loader):
    hosts = ["maya"]

    def __init__(self, context):
        super(Loader, self).__init__(context)
        self.fname = self.fname.replace(
            api.registered_root(), "$AVALON_PROJECTS"
        )


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

    self._events[_on_scene_open] = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kAfterOpen, _on_scene_open
    )

    logger.info("Installed event handler _on_scene_save..")
    logger.info("Installed event handler _before_scene_save..")
    logger.info("Installed event handler _on_scene_new..")
    logger.info("Installed event handler _on_maya_initialized..")
    logger.info("Installed event handler _on_scene_open..")


def _register_events():

    api.on("taskChanged", _on_task_changed)

    logger.info("Installed event callback for 'taskChanged'..")


def _on_maya_initialized(*args):
    api.emit("init", args)

    if cmds.about(batch=True):
        logger.warning("Running batch mode ...")
        return

    # Keep reference to the main Window, once a main window exists.
    self._parent = {
        widget.objectName(): widget
        for widget in QtWidgets.QApplication.topLevelWidgets()
    }["MayaWindow"]


def _on_scene_new(*args):
    api.emit("new", args)


def _on_scene_save(*args):
    api.emit("save", args)


def _on_scene_open(*args):
    api.emit("open", args)


def _before_scene_save(return_code, client_data):

    # Default to allowing the action. Registered
    # callbacks can optionally set this to False
    # in order to block the operation.
    OpenMaya.MScriptUtil.setBool(return_code, True)

    api.emit("before_save", [return_code, client_data])


def _on_task_changed(*args):

    _update_menu_task_label()

    workdir = api.Session["AVALON_WORKDIR"]
    if os.path.exists(workdir):
        logger.info("Updating Maya workspace for task change to %s", workdir)

        _set_project()

        # Set Maya fileDialog's start-dir to /scenes
        frule_scene = cmds.workspace(fileRuleEntry="scene")
        cmds.optionVar(stringValue=("browserLocationmayaBinaryscene",
                                    workdir + "/" + frule_scene))

    else:
        logger.warning("Can't set project for new context because "
                       "path does not exist: %s", workdir)
