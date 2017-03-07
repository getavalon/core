import os
import sys
import uuid

import pyblish.api
from maya import cmds, OpenMaya

from . import lib
from .. import api
from ..vendor.Qt import QtCore, QtWidgets

self = sys.modules[__name__]
self._menu = "mindbenderCore"
self._id_callback = None


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
    api.deregister_data("name")
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

        cmds.menuItem("Show Creator", command=creator.show)
        cmds.menuItem("Show Loader", command=loader.show)
        cmds.menuItem("Show Manager", command=manager.show)

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
        cmds.menuItem("Clone (World)", command=interactive.clone_localspace)
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
    api.register_data(key="name", value="{name}")
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
            "startFrame": cmds.playbackOptions(query=True,
                                               animationStartTime=True),
            "endFrame": cmds.playbackOptions(query=True,
                                             animationEndTime=True),
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

        api.schema.validate(data, "container")

        yield data


def load(asset, subset, version=None, representation=None):
    """Load data into Maya

    Arguments:
        asset ("mindbender-core:asset-1.0"): Asset which to import
        subset ("mindbender-core:subset-1.0"): Subset within Asset to import
        version ("mindbender-core:version-1.0", optional): Defaults to
            latest version.
        representation ("mindbender-core:representation-1.0", optional):
            File format, e.g. `.ma`, `.obj`, `.exr`. String may also
            be provided.

    Returns:
        Newly created objects

    Raises:
        IndexError on no version found
        ValueError on no supported representation

    """

    assert asset["schema"] == "mindbender-core:asset-1.0"
    assert subset["schema"] == "mindbender-core:subset-1.0"

    try:
        if isinstance(version, dict):
            pass

        elif version is None:
            # Not passing a version retusn last
            version = subset["versions"][-1]

        else:
            # Find the version matching the provided number
            version = next(
                v for v in subset["versions"]
                if v["version"] == version
            )

    except (IndexError, StopIteration):
        raise IndexError("\"%s\" of \"%s\" not found." % (version, subset))

    try:
        supported_formats = api.registered_formats()

        representation = next(
            rep for rep in version["representations"]
            if rep["format"] == representation or
            rep["format"] in supported_formats
        )

    except StopIteration:
        formats = list(r["format"] for r in version["representations"])
        raise ValueError(
            "No supported representations.\n\n"
            "Available representations:\n%s\n\n"
            "Supported representations:\n%s"
            % ("\n- ".join(formats),
               "\n- ".join(supported_formats))
        )

    for Loader in api.discover_loaders():
        for family in version.get("families", list()):
            if family in Loader.families:
                print("Running '%s' on '%s'" % (
                    Loader.__name__, asset["name"]))

                return Loader().process(
                    asset=asset,
                    subset=subset,
                    version=version,
                    representation=representation,
                )

    raise ValueError("No loader triggered, check your "
                     "api.registered_loaders_path()")


def create(name, family, options=None):
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
        try:
            data[key] = str(value).format(
                name=name,
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

    asset = None
    subset = None
    version_ = None
    representation = None

    for asset in api.ls(silos=[container["silo"]]):
        if asset["name"] != container["asset"]:
            continue

        for subset in asset["subsets"]:
            if subset["name"] != container["subset"]:
                continue

            try:
                version_ = subset["versions"][version - 1]
            except IndexError:
                raise IndexError("Version '%s' does not exist." % version)

            for representation in version_["representations"]:
                if representation["format"] == container["representation"]:
                    break

            if subset["name"] == container["subset"]:
                break

        if asset["name"] == container["asset"]:
            break

    assert all([asset, subset, version_, representation]), (
        "Could not fully qualify container in available assets.\n"
        "This is a bug.\n"
        "\n"
        "Data\n"
        "asset: %s\n"
        "subset: %s\n"
        "version: %s\n"
        "representation: %s\n" % (asset, subset, version_, representation)
    )

    fname = representation["path"].format(
        dirname=version_["path"].format(root=api.registered_root()),
        format=representation["format"]
    )

    file_type = {
        ".ma": "mayaAscii",
        ".mb": "mayaBinary",
        ".abc": "Alembic"
    }.get(representation["format"])

    assert file_type, ("Unsupported representation: %s" % representation)

    print("Grading '{name}' from '{from_}' to '{to_}' with '{fname}'".format(
        name=container["name"],
        from_=container["version"],
        to_=version,
        fname=fname
    ))

    cmds.file(fname, loadReference=reference_node, type=file_type)

    # Update metadata
    cmds.setAttr(container["objectName"] + ".version", version_["version"])
    cmds.setAttr(container["objectName"] + ".path",
                 version_["path"],
                 type="string")
    cmds.setAttr(container["objectName"] + ".source",
                 version_["source"],
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

    fname = cmds.referenceQuery(reference_node, filename=True)
    cmds.file(fname, removeReference=True)


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
