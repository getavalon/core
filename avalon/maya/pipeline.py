import os
import sys
import uuid
import importlib

from maya import cmds, OpenMaya
from pyblish import api as pyblish

from . import lib, commands
from .. import api, io
from ..vendor import six
from ..vendor.Qt import QtCore, QtWidgets

self = sys.modules[__name__]
self._menu = api.session["label"] + "menu"  # Unique name of menu
self._events = dict()  # Registered Maya callbacks
self._parent = None  # Main Window


def install(config):
    """Install Maya-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(maya)`.

    """

    _register_callbacks()
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


def uninstall():
    _uninstall_menu()

    pyblish.deregister_host("mayabatch")
    pyblish.deregister_host("mayapy")
    pyblish.deregister_host("maya")


def _install_menu():
    from ..tools import (
        creator,
        loader,
        manager,
        publish,
        cbloader,
        cbsceneinventory
    )

    from . import interactive

    _uninstall_menu()

    def deferred():
        cmds.menu(self._menu,
                  label=api.session["label"],
                  tearOff=True,
                  parent="MayaWindow")

        cmds.menuItem("Create...",
                      command=lambda *args: creator.show(parent=self._parent))
        cmds.menuItem("Load... (new)",
                      command=lambda *args: cbloader.show(parent=self._parent))
        cmds.menuItem("Load... (old)",
                      command=lambda *args: loader.show(parent=self._parent))
        cmds.menuItem("Publish...",
                      command=lambda *args: publish.show(parent=self._parent),
                      image=publish.ICON)
        cmds.menuItem("Manage... (new)",
                      command=lambda *args: cbsceneinventory.show(
                          parent=self._parent))
        cmds.menuItem("Manage... (old)",
                      command=lambda *args: manager.show(parent=self._parent))

        cmds.menuItem(divider=True)

        cmds.menuItem("System",
                      label="System",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Reload Pipeline", command=_reload)

        cmds.setParent("..", menu=True)

        cmds.menuItem("Reset Frame Range",
                      command=interactive.reset_frame_range)
        cmds.menuItem("Reset Resolution",
                      command=interactive.reset_resolution)

    # Allow time for uninstallation to finish.
    QtCore.QTimer.singleShot(100, deferred)


def _reload(*args):
    """Attempt to reload pipeline at run-time.

    CAUTION: This is primarily for development and debugging purposes.

    """

    from avalon import api, pipeline, io, lib
    import avalon.maya
    import avalon.maya.pipeline
    import avalon.maya.interactive
    import avalon.maya.commands
    import avalon.tools.creator.app
    import avalon.tools.manager.app
    import avalon.tools.loader.app

    api.uninstall()

    for module in (io,
                   lib,
                   pipeline,
                   avalon.maya.commands,
                   avalon.maya.interactive,
                   avalon.maya.pipeline,
                   avalon.maya.lib,
                   avalon.tools.loader.app,
                   avalon.tools.creator.app,
                   avalon.tools.manager.app,
                   api,
                   avalon.maya):
        reload(module)

    api.install(avalon.maya)


def _uninstall_menu():
    app = QtWidgets.QApplication.instance()
    widgets = dict((w.objectName(), w) for w in app.allWidgets())
    menu = widgets.get(self._menu)

    if menu:
        menu.deleteLater()
        del(menu)


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
        nodes (list): Long names of nodes to containerise
        namespace (str): Namespace under which to host container
        asset (avalon-core:asset-1.0): Current asset
        subset (avalon-core:subset-1.0): Current subset
        version (avalon-core:version-1.0): Current version
        representation (avalon-core:representation-1.0): ...
        loader (str, optional): Name of loader used to produce this container.
        suffix (str, optional): Suffix of container, defaults to `_CON`.

    Returns:
        container (str): Name of container assembly

    """

    container = cmds.sets(nodes, name="%s_%s_%s" % (namespace, name, suffix))

    data = [
        ("id", "pyblish.avalon.container"),
        ("name", name),
        ("namespace", namespace),
        ("loader", str(loader)),
        ("project", context["project"]["name"]),
        ("asset", context["asset"]["name"]),
        ("subset", context["subset"]["name"]),
        ("version", context["version"]["name"]),
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

    for container in sorted(lib.lsattr("id", "pyblish.avalon.container")):
        data = lib.read(container)

        try:
            document = io.find_one(
                {"_id": io.ObjectId(data["representation"])}
            )
        except io.InvalidId:
            api.logger.warning("Skipping %s, invalid id." % container)
            continue

        data = dict(
            schema="avalon-core:container-1.0",
            objectName=container,
            name=data["name"],
            namespace=data["namespace"],
            representation=data["representation"],
            **document["data"]
        )

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
        loader.process(name, namespace, context, data)
    except OSError as e:
        print("WARNING: %s" % e)
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
        Instance as str

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
                plugin.process()
        except Exception as e:
            print("WARNING: %s" % e)
            continue

        plugins.append(plugin)

    assert plugins, "No Creator plug-ins were run, this is a bug"


def _create(name, family, asset=None, options=None, data=None):

    family_ = api.registered_families().get(family)

    assert family_ is not None, "{0} is not a valid family".format(
        family)

    # Merge incoming with existing data
    # TODO(marcus): This is being delegated to Creator plug-ins.
    data = dict(
        dict(api.registered_data(), **family_.get("data", {})),
        **(data or {})
    )

    instance = "%s_SET" % name
    asset = asset or os.environ["AVALON_ASSET"]

    if cmds.objExists(instance):
        raise NameError("\"%s\" already exists." % instance)

    with lib.maintained_selection():
        nodes = list()

        if (options or {}).get("useSelection"):
            nodes = cmds.ls(selection=True)

        instance = cmds.sets(nodes, name=instance)

    # Resolve template
    for key, value in data.items():
        if isinstance(value, basestring):
            try:
                data[key] = str(value).format(
                    subset=name,
                    asset=asset,
                    family=family_["name"]
                )
            except KeyError as e:
                raise KeyError("Invalid dynamic property: %s" % e)

    lib.imprint(instance, data)

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
    cmds.setAttr(container["objectName"] + ".version",
                 new_version["name"])
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

    print("Removing '%s' from Maya.." % container["name"])

    namespace = cmds.referenceQuery(reference_node, namespace=True)
    fname = cmds.referenceQuery(reference_node, filename=True)
    cmds.file(fname, removeReference=True)

    try:
        # If container is not automatically cleaned up by May (issue #118)
        cmds.namespace(removeNamespace=namespace, deleteNamespaceContent=True)
    except RuntimeError:
        pass


def _register_callbacks():
    for handler, event in self._events.copy().items():
        if event is None:
            continue

        try:
            OpenMaya.MMessage.removeCallback(event)
            self._events[handler] = None
        except RuntimeError, e:
            print(e)

    self._events[_on_scene_save] = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kBeforeSave, _on_scene_save
    )

    self._events[_on_scene_new] = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kAfterNew, _on_scene_new
    )

    self._events[_on_maya_initialized] = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kMayaInitialized, _on_maya_initialized
    )

    print("Installed event handler _on_scene_save..")
    print("Installed event handler _on_scene_new..")
    print("Installed event handler _on_maya_initialized..")


def _set_uuid(node):
    """Add mbID to `node`

    Unless one already exists.

    """

    attr = "{0}.mbID".format(node)

    if not cmds.objExists(attr):
        cmds.addAttr(node, longName="mbID", dataType="string")
        _, uid = str(uuid.uuid4()).rsplit("-", 1)
        cmds.setAttr(attr, uid, type="string")


def _on_maya_initialized(_):
    print("Running callback: maya initialized..")
    commands.reset_frame_range()
    commands.reset_resolution()

    # Keep reference to the main Window, once a main window exists.
    self._parent = {
        widget.objectName(): widget
        for widget in QtWidgets.QApplication.topLevelWidgets()
    }["MayaWindow"]


def _on_scene_new(_):
    print("Running callback: scene new..")

    # Load dependencies
    # TODO(marcus): Externalise this
    cmds.loadPlugin("AbcExport.mll", quiet=True)
    cmds.loadPlugin("AbcImport.mll", quiet=True)

    commands.reset_frame_range()
    commands.reset_resolution()


def _on_scene_save(_):
    """Automatically add IDs to new nodes

    Any transform of a mesh, without an exising ID,
    is given one automatically on file save.

    """

    print("Running callback: scene save..")

    nodes = (set(cmds.ls(type="mesh", long=True)) -
             set(cmds.ls(long=True, readOnly=True)) -
             set(cmds.ls(long=True, lockedNodes=True)))

    transforms = cmds.listRelatives(list(nodes), parent=True) or list()

    # Add unique identifiers
    for node in transforms:
        _set_uuid(node)
