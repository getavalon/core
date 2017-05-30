import os
import sys
import uuid

import pyblish.api
from maya import cmds, OpenMaya

from . import lib
from .. import api, io
from ..vendor.Qt import QtCore, QtWidgets

self = sys.modules[__name__]
self._menu = "mindbenderCore"
self._id_callback = None
self._parent = {
    o.objectName(): o
    for o in QtWidgets.QApplication.topLevelWidgets()
}.get("MayaWindow")


def install():
    """Install Maya-specific functionality of mindbender-core.

    This function is called automatically on calling `api.install(maya)`.

    """

    try:
        import pyblish_maya
        assert pyblish_maya.is_setup()

    except (ImportError, AssertionError):
        raise ImportError("mindbender-core depends on pyblish-maya.")

    _install_menu()

    _register_data()
    _register_formats()
    _register_plugins()
    _register_loaders()
    _register_families()

    _register_id_callback()


def uninstall():
    _uninstall_menu()

    api.deregister_format(".ma")
    api.deregister_format(".mb")
    api.deregister_format(".abc")

    api.deregister_data("id")
    api.deregister_data("subset")
    api.deregister_data("family")

    api.deregister_family("mindbender.model")
    api.deregister_family("mindbender.rig")
    api.deregister_family("mindbender.animation")
    api.deregister_family("mindbender.lookdev")


def _install_menu():
    from ..tools import (
        creator,
        loader,
        manager
    )

    from . import interactive

    _uninstall_menu()

    def deferred():
        cmds.menu(self._menu,
                  label="Mindbender",
                  tearOff=True,
                  parent="MayaWindow")

        cmds.menuItem("Show Creator",
                      command=lambda *args: creator.show(parent=self._parent))
        cmds.menuItem("Show Loader",
                      command=lambda *args: loader.show(parent=self._parent))
        cmds.menuItem("Show Manager",
                      command=lambda *args: manager.show(parent=self._parent))

        cmds.menuItem(divider=True)

        # Modeling sub-menu
        cmds.menuItem("Modeling",
                      label="Modeling",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Combine", command=interactive.combine)

        # Rigging sub-menu
        cmds.menuItem("Rigging",
                      label="Rigging",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Auto Connect", command=interactive.auto_connect)
        cmds.menuItem("Clone (Local)", command=interactive.clone_localspace)
        cmds.menuItem("Clone (World)", command=interactive.clone_worldspace)
        cmds.menuItem("Clone (Special)", command=interactive.clone_special)
        cmds.menuItem("Create Follicle", command=interactive.follicle)

        # Animation sub-menu
        cmds.menuItem("Animation",
                      label="Animation",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Set Defaults", command=interactive.set_defaults)

        cmds.setParent("..", menu=True)

        cmds.menuItem(divider=True)

        cmds.menuItem("Auto Connect", command=interactive.auto_connect_assets)
        cmds.menuItem("Reset Frame Range",
                      command=interactive.reset_frame_range)

    # Allow time for uninstallation to finish.
    QtCore.QTimer.singleShot(100, deferred)


def _uninstall_menu():
    app = QtWidgets.QApplication.instance()
    widgets = dict((w.objectName(), w) for w in app.allWidgets())
    menu = widgets.get(self._menu)

    if menu:
        menu.deleteLater()
        del(menu)


def _register_data():
    # Default Instance data
    # All newly created instances will be imbued with these members.
    api.register_data(key="id", value="pyblish.mindbender.instance")
    api.register_data(key="subset", value="{name}")
    api.register_data(key="family", value="{family}")


def _register_formats():
    # These file-types will appear in the Loader GUI
    api.register_format(".ma")
    api.register_format(".mb")
    api.register_format(".abc")


def _register_families():
    # These families will appear in the Creator GUI
    api.register_family(
        name="mindbender.model",
        label="Model",
        help="Polygonal geometry for animation",
    )

    api.register_family(
        name="mindbender.rig",
        label="Rig",
        help="Character rig",
    )

    api.register_family(
        name="mindbender.lookdev",
        label="Look",
        help="Shaders, textures and look",
    )

    api.register_family(
        name="mindbender.historyLookdev",
        label="History Look",
        help="Shaders, textures and look with History",
    )

    api.register_family(
        name="mindbender.animation",
        label="Animation",
        help="Any character or prop animation",
        data={
            "startFrame": lambda: cmds.playbackOptions(
                query=True, animationStartTime=True),
            "endFrame": lambda: cmds.playbackOptions(
                query=True, animationEndTime=True),
        }
    )


def _register_plugins():
    lib_py_path = sys.modules[__name__].__file__
    package_path = os.path.dirname(lib_py_path)
    plugin_path = os.path.join(package_path, "plugins")
    pyblish.api.register_plugin_path(plugin_path)


def _register_loaders():
    lib_py_path = sys.modules[__name__].__file__
    package_path = os.path.dirname(lib_py_path)
    loaders_path = os.path.join(package_path, "loaders")
    api.register_loader_path(loaders_path)


def ls():
    """List containers from active Maya scene

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Maya; once loaded
    they are called 'containers'

    """

    for container in sorted(lib.lsattr("id", "pyblish.mindbender.container")):
        data = dict(
            schema="mindbender-core:container-1.0",
            objectName=container,
            **lib.read(container)
        )

        # api.schema.validate(data, "container")

        yield data


def load(representation):
    """Load asset via database

    Arguments:
        representation (bson.objectid.ObjectId): Address to representation

    """

    if not isinstance(representation, io.ObjectId):
        representation = io.ObjectId(representation)

    representation = io.find_one({"_id": representation})
    version = io.find_one({"_id": representation["parent"]})
    subset = io.find_one({"_id": version["parent"]})
    asset = io.find_one({"_id": subset["parent"]})
    project = io.find_one({"_id": asset["parent"]})

    for Loader in api.discover_loaders():
        if not any(family in Loader.families
                   for family in version["data"].get("families", list)):
            continue

        print("Running '%s' on '%s'" % (Loader.__name__, asset["name"]))

        return Loader().process(
            project=project,
            asset=asset,
            subset=subset,
            version=version,
            representation=representation,
        )


def create(asset, name, family, options=None):
    """Create new instance

    Associate nodes with a name and family. These nodes are later
    validated, according to their `family`, and integrated into the
    shared environment, relative their `name`.

    Data relative each family, along with default data, are imprinted
    into the resulting objectSet. This data is later used by extractors
    and finally asset browsers to help identify the origin of the asset.

    Arguments:
        name (str): Name of instance
        family (str): Name of family
        options (dict, optional): Additional options

    Raises:
        NameError on `name` already exists
        KeyError on invalid dynamic property
        RuntimeError on host error

    Returns:
        Instance as str

    """

    family_ = api.registered_families().get(family)

    assert family_ is not None, "{0} is not a valid family".format(
        family)

    data = dict(api.registered_data(), **family_.get("data", {}))
    data["asset"] = asset

    instance = "%s_SET" % name

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
                    name=name,
                    family=family_["name"]
                )
            except KeyError as e:
                raise KeyError("Invalid dynamic property: %s" % e)

    print("About to imprint")
    lib.imprint(instance, data)

    return instance


def update(container, version=-1):
    """Update `container` to `version`

    This function relies on a container being referenced. At the time of this
    writing, all assets - models, rigs, animations, shaders - are referenced
    and should pose no problem. But should there be an asset that isn't
    referenced then this function will need to see an update.

    Arguments:
        container (mindbender-core:container-1.0): Container to update,
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
    cmds.setAttr(container["objectName"] + ".source",
                 new_version["data"]["source"],
                 type="string")


def remove(container):
    """Remove an existing `container` from Maya scene

    Arguments:
        container (mindbender-core:container-1.0): Which container
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


def _register_id_callback():
    """Automatically add IDs to new nodes

    Any transform of a mesh, without an exising ID,
    is given one automatically on file save.

    """

    if self._id_callback is not None:
        try:
            OpenMaya.MMessage.removeCallback(self._id_callback)
            self._id_callback = None
        except RuntimeError, e:
            print(e)

    self._id_callback = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kBeforeSave, _callback
    )

    print("Registered _callback")


def _set_uuid(node):
    """Add mbID to `node`

    Unless one already exists.

    """

    attr = "{0}.mbID".format(node)

    if not cmds.objExists(attr):
        cmds.addAttr(node, longName="mbID", dataType="string")
        _, uid = str(uuid.uuid4()).rsplit("-", 1)
        cmds.setAttr(attr, uid, type="string")


def _callback(_):
    nodes = (set(cmds.ls(type="mesh", long=True)) -
             set(cmds.ls(long=True, readOnly=True)) -
             set(cmds.ls(long=True, lockedNodes=True)))

    transforms = cmds.listRelatives(list(nodes), parent=True) or list()

    # Add unique identifiers
    for node in transforms:
        _set_uuid(node)
