import os
import sys
import logging

from .. import api
from ..vendor.Qt import QtWidgets, QtGui, QtCore

from maya import cmds

from . import lib

self = sys.modules[__name__]
self.log = logging.getLogger("pyblish-mindbender")
self.menu = "pyblishMindbender"


def install():
    try:
        import pyblish_maya
        assert pyblish_maya.is_setup()

    except (ImportError, AssertionError):
        _display_missing_dependencies()

    _install_menu()

    # Mindbender integrates to "root", which we define to be the PROJECT,
    # the full path to a project. PROJECTDIR is set during application launch,
    # via the corresponding .bat file

    project = os.getenv("PROJECTDIR")
    assert project, "Missing environment variable 'PROJECTDIR'"
    api.register_root(project)

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
    from mindbender.tools import creator, loader

    _uninstall_menu()

    def deferred():
        cmds.menu(self.menu,
                  label="Pipeline",
                  tearOff=True,
                  parent="MayaWindow")
        cmds.menuItem("Show Creator", command=creator.show)
        cmds.menuItem("Show Loader", command=loader.show)

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
    for container in lib.lsattr("id", "pyblish.mindbender.container"):
        data = dict(
            schema="pyblish-mindbender:container-1.0",
            name=container,
            **lib.read(container)
        )

        api.schema.validate(data, "container")

        yield data


def load(asset, subset, version=-1, representation=None):
    """Load data into Maya

    Arguments:
        asset ("pyblish-mindbender:asset-1.0"): Asset which to import
        subset ("pyblish-mindbender:subset-1.0"): Subset within Asset to import
        version (int, optional): Version number, defaults to latest
        representation (str, optional): File format, e.g. `.ma`, `.obj`, `.exr`

    Returns:
        Reference node

    Raises:
        IndexError on no version found
        ValueError on no supported representation

    """

    assert subset["schema"] == "pyblish-mindbender:subset-1.0"
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


def containerise(name, namespace, nodes, version, suffix="_CON"):
    """Bundle `nodes` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        nodes (list): Long names of nodes to containerise
        namespace (str): Namespace under which to host container
        version (pyblish-mindbender:version-1.0): Current version

    Returns:
        container (str): Name of container assembly

    """

    container = cmds.sets(nodes, name=namespace + ":" + name + suffix)

    data = [
        ("id", "pyblish.mindbender.container"),
        ("author", version["author"]),
        ("loader", self.__name__),
        ("families", " ".join(version.get("families", list()))),
        ("time", version["time"]),
        ("version", version["version"]),
        ("path", version["path"]),
        ("source", version["source"]),
        ("comment", version.get("comment", ""))
    ]

    for key, value in data:

        if not value:
            continue

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
        "pyblish-mindbender requires pyblish-maya.\n"
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

        "See https://github.com/pyblish/pyblish-mindbender "
        "for more information."
    )

    messagebox.setStandardButtons(messagebox.Ok)
    messagebox.exec_()

    raise RuntimeError("pyblish-mindbender requires pyblish-maya "
                       "to have been setup.")
