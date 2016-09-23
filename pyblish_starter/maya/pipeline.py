import os
import sys
import logging

from .. import pipeline
from ..vendor.Qt import QtWidgets, QtGui

from maya import cmds

self = sys.modules[__name__]
self.log = logging.getLogger()
self.menu = "pyblishStarter"


def install():
    try:
        import pyblish_maya
        assert pyblish_maya.is_setup()

    except (ImportError, AssertionError):
        _display_missing_dependencies()

    install_menu()
    register_formats()


def uninstall():
    uninstall_menu()
    deregister_formats()


def install_menu():
    from pyblish_starter.tools import creator, loader

    uninstall_menu()

    cmds.menu(self.menu,
              label="Pyblish Starter",
              tearOff=True,
              parent="MayaWindow")
    cmds.menuItem("Show Creator", command=creator.show)
    cmds.menuItem("Show Loader", command=loader.show)


def uninstall_menu():
    widgets = dict((w.objectName(), w) for w in QtWidgets.qApp.allWidgets())
    menu = widgets.get(self.menu)

    if menu:
        menu.deleteLater()
        del(menu)


def register_formats():
    pipeline.register_format(".ma")
    pipeline.register_format(".mb")
    pipeline.register_format(".abc")


def deregister_formats():
    pipeline.deregister_format(".ma")
    pipeline.deregister_format(".mb")
    pipeline.deregister_format(".abc")


def root():
    """Return project-root or directory of current working file"""
    return (cmds.workspace(rootDirectory=True, query=True) or
            cmds.workspace(directory=True, query=True))


def load(asset, version=-1):
    """Load asset

    Arguments:
        asset (dict): Object of schema "pyblish-starter:asset-1.0"
        version (int, optional): Version number, defaults to latest

    Returns:
        Reference node

    Raises:
        IndexError on version not found
        ValueError on no supported representation

    """

    assert asset["schema"] == "pyblish-starter:asset-1.0"
    assert isinstance(version, int), "Version must be integer"

    try:
        version = asset["versions"][version]
    except IndexError:
        raise IndexError("\"%s\" of \"%s\" not found." % (version, asset))

    supported_formats = pipeline.registered_formats()

    # Pick any compatible representation.
    # Hint: There's room to make the user choose one of many.
    #   Such as choosing between `.obj` and `.ma` and `.abc`,
    #   each compatible but different.
    try:
        representation = next(rep for rep in version["representations"]
                              if rep["format"] in supported_formats)
    except StopIteration:
        raise ValueError(
            "No supported representations for %s\n"
            "Supported representations: %s" % (
                asset["name"],
                ", ".join(r["format"] for r in version["representations"]))
        )

    fname = representation["path"].format(
        dirname=asset["path"],
        format=representation["format"]
    )

    nodes = cmds.file(fname,
                      namespace=asset["name"] + "_",
                      reference=True)

    return cmds.referenceQuery(nodes, referenceNode=True)


def create(name, family):
    """Create new instance

    Arguments:
        name (str): Name of instance
        family (str): Name of family
        use_selection (bool): Use selection to create this instance?

    """

    for item in pipeline.registered_families():
        if item["name"] == family:
            break

    assert item is not None, "{0} is not a valid family".format(family)

    print("%s + %s" % (pipeline.registered_data(), item.get("data", [])))

    data = pipeline.registered_data() + item.get("data", [])
    instance = "%s_SEL" % name

    if cmds.objExists(instance):
        raise NameError("\"%s\" already exists." % instance)

    # Include selection
    instance = cmds.sets(name=instance)

    for item in data:
        key = item["key"]

        try:
            value = item["value"].format(
                name=name,
                family=family
            )
        except KeyError as e:
            raise KeyError("Invalid dynamic property: %s" % e)

        if isinstance(value, bool):
            add_type = {"attributeType": "bool"}
            set_type = {"keyable": False, "channelBox": True}
        elif isinstance(value, basestring):
            add_type = {"dataType": "string"}
            set_type = {"type": "string"}
        elif isinstance(value, int):
            add_type = {"attributeType": "long"}
            set_type = {"keyable": False, "channelBox": True}
        elif isinstance(value, float):
            add_type = {"attributeType": "double"}
            set_type = {"keyable": False, "channelBox": True}
        else:
            raise TypeError("Unsupported type: %r" % type(value))

        cmds.addAttr(instance, ln=key, **add_type)
        cmds.setAttr(instance + "." + key, value, **set_type)

    cmds.select(instance, noExpand=True)

    return instance


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

        messagebox.setInformativeText("""\
pyblish-starter requires pyblish-maya.\
""")

        messagebox.setDetailedText("""\
1) Install Pyblish for Maya

   $ pip install pyblish-maya

2) Run setup()

   >>> import pyblish_maya
   >>> pyblish_maya.setup()

3) Try again.

   >>> pyblish_starter.install()

See https://github.com/pyblish/pyblish-starter for more information.
""")

        messagebox.setStandardButtons(messagebox.Ok)
        messagebox.exec_()

        raise RuntimeError("pyblish-starter requires pyblish-maya "
                           "to have been setup.")
