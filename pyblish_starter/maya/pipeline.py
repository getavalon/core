import os
import sys
import logging

from .. import api
from ..vendor.Qt import QtWidgets, QtGui, QtCore

from maya import cmds

from . import lib

self = sys.modules[__name__]
self.log = logging.getLogger("pyblish-starter")
self.menu = "pyblishStarter"


def install():
    try:
        import pyblish_maya
        assert pyblish_maya.is_setup()

    except (ImportError, AssertionError):
        _display_missing_dependencies()

    _install_menu()
    _register_formats()
    _register_root()


def uninstall():
    _uninstall_menu()
    _deregister_formats()


def _install_menu():
    from pyblish_starter.tools import creator, loader

    _uninstall_menu()

    def deferred():
        cmds.menu(self.menu,
                  label="Pyblish Starter",
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


def _register_formats():
    api.register_format(".ma")
    api.register_format(".mb")
    api.register_format(".abc")


def _deregister_formats():
    api.deregister_format(".ma")
    api.deregister_format(".mb")
    api.deregister_format(".abc")


def _register_root():
    """Register project root or directory of current working file"""
    root = (
        cmds.workspace(rootDirectory=True, query=True) or
        cmds.workspace(directory=True, query=True)
    )

    api.register_root(root)


def ls():
    """List loaded assets"""
    for container in cmds.ls("*.id",
                             type="transform",
                             objectsOnly=True,
                             long=True):
        data = dict(
            schema="pyblish-starter:container-1.0",
            path=container,
            **lib.read(container)
        )

        api.schema.validate(data, "container")

        yield data


def load(asset, version=-1):
    """Load asset

    Arguments:
        asset ("pyblish-starter:asset-1.0"): Asset which to import
        version (int, optional): Version number, defaults to latest

    Returns:
        Reference node

    Raises:
        IndexError on no version found
        ValueError on no supported representation

    """

    assert asset["schema"] == "pyblish-starter:asset-1.0"
    assert isinstance(version, int), "Version must be integer"

    try:
        version = asset["versions"][version]
    except IndexError:
        raise IndexError("\"%s\" of \"%s\" not found." % (version, asset))

    supported_formats = api.registered_formats()

    # Pick any compatible representation.
    # Hint: There's room to make the user choose one of many.
    #   Such as choosing between `.obj` and `.ma` and `.abc`,
    #   each compatible but different.
    try:
        representation = next(
            rep for rep in version["representations"]
            if rep["format"] in supported_formats and
            rep["path"] != "{dirname}/source{format}"
        )

    except StopIteration:
        formats = list(r["format"] for r in version["representations"])
        raise ValueError(
            "No supported representations for \"%s\"\n\n"
            "Supported representations: %s"
            % (asset["name"], "\n- ".join(formats)))

    fname = representation["path"].format(
        dirname=version["path"],
        format=representation["format"]
    )

    nodes = cmds.file(fname,
                      namespace=asset["name"] + "_",
                      reference=True,
                      returnNewNodes=True)

    self.log.info("Containerising \"%s\".." % fname)
    containerise(asset["name"], nodes, version)

    self.log.info("Container created, returning reference node.")
    return cmds.referenceQuery(nodes[0], referenceNode=True)


def create(name, family):
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

    Raises:
        NameError on `name` already exists
        KeyError on invalid dynamic property
        RuntimeError on host error

    """

    for item in api.registered_families():
        if item["name"] == family:
            break

    assert item is not None, "{0} is not a valid family".format(family)

    data = api.registered_data() + item.get("data", [])

    # Convert to dictionary
    data = dict((i["key"], i["value"]) for i in data)

    instance = "%s_SEL" % name

    if cmds.objExists(instance):
        raise NameError("\"%s\" already exists." % instance)

    instance = cmds.sets(name=instance)

    # Resolve template
    for key, value in data.items():
        try:
            data[key] = value.format(
                name=name,
                family=family
            )
        except KeyError as e:
            raise KeyError("Invalid dynamic property: %s" % e)

    lib.imprint(instance, data)
    cmds.select(instance, noExpand=True)

    return instance


def containerise(name, nodes, version):
    """Bundle `nodes` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        nodes (list): Long names of nodes to containerise
        version (pyblish-starter:version-1.0): Current version

    """

    assemblies = cmds.ls(nodes, assemblies=True)
    container = cmds.group(assemblies, name=name)

    data = [
        ("id", "pyblish.starter.container"),
        ("author", version["author"]),
        ("loader", self.__name__),
        ("time", version["time"]),
        ("version", version["version"]),
        ("source", version["source"]),
        ("comment", version.get("comment", ""))
    ]

    for key, value in data:

        if not value:
            continue

        cmds.addAttr(container, longName=key, dataType="string")
        cmds.setAttr(container + "." + key, value, type="string")

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
            "pyblish-starter requires pyblish-maya.\n"
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
            ">>> pyblish_starter.install()\n"

            "See https://github.com/pyblish/pyblish-starter "
            "for more information."
        )

        messagebox.setStandardButtons(messagebox.Ok)
        messagebox.exec_()

        raise RuntimeError("pyblish-starter requires pyblish-maya "
                           "to have been setup.")
