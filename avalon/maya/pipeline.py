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
                          cbloader.show(parent=self._parent,
                                        use_context=True))
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
    AVALON_CONTAINERS = "AVALON_CONTAINERS"
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

    main_container = cmds.ls(AVALON_CONTAINERS, type="objectSet")
    if not main_container:
        main_container = cmds.sets(empty=True, name=AVALON_CONTAINERS)
    else:
        main_container = main_container[0]

    # addElement requires the set to which the items need to be added to
    cmds.sets(container, addElement=main_container)

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


class Creator(api.Creator):
    def process(self):
        nodes = list()

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


class ReferenceLoader(Loader):
    """A basic loader that loads a Maya reference
    
    For backwards compatibility you can update your old Maya loaders from this
    and it should work with the new loader methodology without `host.load`, 
    `host.remove` and `host.update`. All you need to implement is the same
    `process()` method as before.
    
    """

    representations = ["ma", "mb", "abc"]

    # Extension to maya file type conversion - for `update()` method
    file_types = {
        "ma": "mayaAscii",
        "mb": "mayaBinary",
        "abc": "Alembic"
    }

    def load(self,
             context,
             name=None,
             namespace=None,
             data=None):

        asset = context['asset']['name']
        subset = context['subset']['name']

        name = name or subset
        namespace = namespace or lib.unique_namespace(
            asset + "_",
            prefix="_" if asset[0].isdigit() else "",
            suffix="_",
        )

        try:
            with lib.maintained_selection():
                self.process(name, namespace, context, data)
        except OSError as e:
            logger.info("WARNING: %s" % e)
            return list()

        # Only containerize if any nodes were loaded by the Loader
        nodes = self[:]
        if not nodes:
            return

        return containerise(
            name=name,
            namespace=namespace,
            nodes=nodes,
            context=context,
            loader=self.__class__.__name__)

    def update(self, container, new_representation):
        """
        
        This function relies on a container being referenced. At the time of 
        this writing, all assets - models, rigs, animations, shaders - are 
        referenced and should pose no problem. But should there be an asset 
        that isn't referenced then this function will need to see an update.
        
        """

        fname = api.get_representation_path(new_representation)
        node = container["objectName"]

        # Assume asset has been referenced
        reference_node = next((node for node in cmds.sets(node, query=True)
                               if cmds.nodeType(node) == "reference"), None)

        assert reference_node, ("Imported container not supported; "
                                "container must be referenced.")

        file_type = self.file_types.get(new_representation["name"])

        assert file_type, ("Unsupported representation: %s" %
                           new_representation)

        assert os.path.exists(fname), "%s does not exist." % fname
        cmds.file(fname, loadReference=reference_node, type=file_type)

        # Update metadata
        cmds.setAttr(container["objectName"] + ".representation",
                     str(new_representation["_id"]),
                     type="string")

    def remove(self, container):
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
            cmds.namespace(removeNamespace=namespace,
                           deleteNamespaceContent=True)
        except RuntimeError:
            pass

    def process(self, name, namespace, context, data):
        """This method is here to preserve backwards compatibility.
        
        
        """
        self.log.error("When inheriting from `ReferenceLoader` you must "
                       "implement the `process()` method.")
        raise RuntimeError("No ReferenceLoader process implemented. "
                           "See log for details.")


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


def _before_scene_save(return_code, client_data):

    # Default to allowing the action. Registered
    # callbacks can optionally set this to False
    # in order to block the operation.
    OpenMaya.MScriptUtil.setBool(return_code, True)

    api.emit("before_save", [return_code, client_data])
