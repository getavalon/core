import os
import sys
import logging

from .. import api
from ..vendor.Qt import QtWidgets, QtGui, QtCore

from maya import cmds

from . import lib

self = sys.modules[__name__]
self.log = logging.getLogger("mindbender-core")
self.menu = "pyblishMindbender"


def install():
    try:
        import pyblish_maya
        assert pyblish_maya.is_setup()

    except (ImportError, AssertionError):
        _display_missing_dependencies()

    _install_menu()

    # Default Instance data
    # All newly created instances will be imbued with these members.
    api.register_data(key="id", value="pyblish.mindbender.instance")
    api.register_data(key="name", value="{name}")
    api.register_data(key="subset", value="{name}")
    api.register_data(key="family", value="{family}")

    # These file-types will appear in the Loader GUI
    api.register_format(".ma")
    api.register_format(".mb")
    api.register_format(".abc")

    # Register default loaders
    lib_py_path = sys.modules[__name__].__file__
    package_path = os.path.dirname(lib_py_path)
    loaders_path = os.path.join(package_path, "loaders")
    api.register_loaders_path(loaders_path)

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


def _install_menu():
    from ..tools import (
        creator,
        loader,
        manager
    )

    from . import interactive

    _uninstall_menu()

    def deferred():
        cmds.menu(self.menu,
                  label="Mindbender",
                  tearOff=True,
                  parent="MayaWindow")

        cmds.menuItem("Show Creator", command=creator.show)
        cmds.menuItem("Show Loader", command=loader.show)
        cmds.menuItem("Show Manager", command=manager.show)

        cmds.menuItem(divider=True)

        def command(func, **kwargs):
            # Maya passes a few additional arguments to#
            # any given function. We squash (ignore) those here.
            return lambda *args: func(**kwargs)

        # Modeling sub-menu
        cmds.menuItem("Modeling",
                      label="Modeling",
                      tearOff=True,
                      subMenu=True,
                      parent=self.menu)

        cmds.menuItem("Combine",
                      command=command(interactive.combine))

        # Rigging sub-menu
        cmds.menuItem("Rigging",
                      label="Rigging",
                      tearOff=True,
                      subMenu=True,
                      parent=self.menu)

        cmds.menuItem("Auto Connect",
                      command=command(interactive.auto_connect))
        cmds.menuItem("Clone (Local)",
                      command=command(interactive.clone, worldspace=False))
        cmds.menuItem("Clone (Worldspace)",
                      command=command(interactive.clone, worldspace=True))
        cmds.menuItem("Clone (Special)",
                      command=command(interactive.clone_with_attributes))
        cmds.menuItem("Create Follicle",
                      command=command(interactive.follicle))

        # Animation sub-menu
        cmds.menuItem("Animation",
                      label="Animation",
                      tearOff=True,
                      subMenu=True,
                      parent=self.menu)

        cmds.menuItem("Set Defaults",
                      command=command(interactive.set_defaults))

    # Allow time for uninstallation to finish.
    QtCore.QTimer.singleShot(100, deferred)


def _uninstall_menu():
    widgets = dict((w.objectName(), w) for w in QtWidgets.qApp.allWidgets())
    menu = widgets.get(self.menu)

    if menu:
        menu.deleteLater()
        del(menu)


def _register_root():
    """Register project root or directory of current working file"""
    root = (
        cmds.workspace(rootDirectory=True, query=True) or
        cmds.workspace(directory=True, query=True)
    )

    api.register_root(root)


def ls():
    """List loaded assets"""
    for container in sorted(lib.lsattr("id", "pyblish.mindbender.container")):
        data = dict(
            schema="mindbender-core:container-1.0",
            objectName=container,
            **lib.read(container)
        )

        api.schema.validate(data, "container")

        yield data


def load(asset, subset, version=-1, representation=None):
    """Load data into Maya

    Arguments:
        asset ("mindbender-core:asset-1.0"): Asset which to import
        subset ("mindbender-core:subset-1.0"): Subset within Asset to import
        version (int, optional): Version number, defaults to latest
        representation (str, optional): File format, e.g. `.ma`, `.obj`, `.exr`

    Returns:
        Reference node

    Raises:
        IndexError on no version found
        ValueError on no supported representation

    """

    assert subset["schema"] == "mindbender-core:subset-1.0"
    assert isinstance(version, int), "Version must be integer"

    try:
        version = subset["versions"][version]
    except IndexError:
        raise IndexError("\"%s\" of \"%s\" not found." % (version, subset))

    if representation is None:
        # TODO(marcus): There's room to make the user choose one of many.
        #   Such as choosing between `.obj` and `.ma` and `.abc`,
        #   each compatible but different.
        representation = api.any_representation(version)

    loaded = False
    for Loader in api.discover_loaders():
        for family in version.get("families", list()):
            if family in Loader.families:
                print("Running '%s' on '%s'" % (
                    Loader.__name__, asset["name"]))

                Loader().process(asset, subset, version, representation)
                loaded = True

    if not loaded:
        cmds.warning("No loader triggered, check your "
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
        ".mb": "alembic"
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


def containerise(name,
                 namespace,
                 nodes,
                 asset,
                 subset,
                 version,
                 representation,
                 suffix="_CON"):
    """Bundle `nodes` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        nodes (list): Long names of nodes to containerise
        namespace (str): Namespace under which to host container
        asset (mindbender-core:asset-1.0): Current asset
        subset (mindbender-core:subset-1.0): Current subset
        version (mindbender-core:version-1.0): Current version

    Returns:
        container (str): Name of container assembly

    """

    container = cmds.sets(nodes, name=namespace + ":" + name + suffix)

    data = [
        ("id", "pyblish.mindbender.container"),
        ("name", namespace),
        ("author", version["author"]),
        ("loader", self.__name__),
        ("families", " ".join(version.get("families", list()))),
        ("time", version["time"]),
        ("asset", asset["name"]),
        ("subset", subset["name"]),
        ("representation", representation["format"]),
        ("version", version["version"]),

        # TEMPORARY, REMOVE PLEASE
        # Temporarily assume "assets", as existing published assets
        # won't have this new variable.
        ("silo", version.get("silo", "assets")),

        ("path", version["path"]),
        ("source", version["source"]),
        ("comment", version.get("comment", ""))
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
    # cmds.setAttr(container + ".verticesOnlySet", True)

    return container


def _display_missing_dependencies():
    import pyblish

    messagebox = QtWidgets.QMessageBox()
    messagebox.setIcon(messagebox.Warning)
    messagebox.setWindowIcon(QtGui.QIcon(os.path.join(
        os.path.dirname(pyblish.__file__),
        "icons",
        "logo-32x32.svg"))
    )

    spacer = QtWidgets.QWidget()
    spacer.setMinimumSize(400, 0)
    spacer.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                         QtWidgets.QSizePolicy.Expanding)

    layout = messagebox.layout()
    layout.addWidget(spacer, layout.rowCount(), 0, 1, layout.columnCount())

    messagebox.setWindowTitle("Uh oh")
    messagebox.setText("Missing dependencies")

    messagebox.setInformativeText(
        "mindbender-core requires pyblish-maya.\n"
    )

    messagebox.setDetailedText(
        "1) Install Pyblish for Maya\n"
        "\n"
        "$ pip install pyblish-maya\n"
        "\n"
        "2) Run setup()\n"
        "\n"
        ">>> import pyblish_maya\n"
        ">>> pyblish_maya.setup()\n"
        "\n"
        "3) Try again.\n"
        "\n"
        ">>> mindbender.install()\n"

        "See https://github.com/mindbender-studio/core "
        "for more information."
    )

    messagebox.setStandardButtons(messagebox.Ok)
    messagebox.exec_()

    raise RuntimeError("mindbender-core requires pyblish-maya "
                       "to have been setup.")
