import os
import sys
import importlib
from .. import api, io
import contextlib
from pyblish import api as pyblish
from ..vendor import toml

from pprint import pprint

from avalon.nuke.logger import nuke_logger

import nuke

# TODO: covert completery fusion pipeline into nuke
# TODO: go to config.nuke.__init__ and again convert fusion to Nuke
# TODO: config.nuke.pipeline convert from fusion

log = nuke_logger(__name__)

self = sys.modules[__name__]
self._parent = None


def reload_pipeline():
    """Attempt to reload pipeline at run-time.

    CAUTION: This is primarily for development and debugging purposes.

    """

    import importlib

    api.uninstall()
    _uninstall_menu()

    for module in ("avalon.io",
                   "avalon.lib",
                   "avalon.pipeline",
                   "avalon.nuke.logger",
                   "avalon.nuke.pipeline",
                   "avalon.nuke.lib",
                   "avalon.tools.loader.app",
                   "avalon.tools.creator.app",
                   "avalon.tools.manager.app",

                   "avalon.api",
                   "avalon.tools",
                   "avalon.nuke"):

        module = importlib.import_module(module)
        reload(module)

    import avalon.nuke
    api.install(avalon.nuke)

    _install_menu()
    _register_events()


def containerise(node,
                 name,
                 namespace,
                 context,
                 node_name=None):
    """Bundle `nodes` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        node (object): The node in Nuke to imprint as container,
        usually a Reader.
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        context (dict): Asset information
        node_name (str, optional): Name of node used to produce this container.

    Returns:
        None

    """

    data = [
        ("schema", "avalon-core:container-2.0"),
        ("id", "pyblish.avalon.container"),
        ("name", str(name)),
        ("namespace", str(namespace)),
        ("node_name", str(node_name)),
        ("representation", str(context["representation"]["_id"])),
    ]

    try:
        avalon = node['avalon'].value()
    except ValueError as error:
        tab = nuke.Tab_Knob("Avalon")
        uk = nuke.Text_Knob('avalon', '')
        node.addKnob(tab)
        node.addKnob(uk)
        log.info("created new user knob avalon")

    node['avalon'].setValue(toml.dumps(data))


def parse_container(node):
    """Returns containerised data of a node

    This reads the imprinted data from `containerise`.

    """

    raw_text_data = node['avalon'].value()
    data = toml.loads(raw_text_data, _dict=dict)

    if not isinstance(data, dict):
        return

    # If not all required data return the empty container
    required = ['schema', 'id', 'name',
                'namespace', 'node_name', 'representation']
    if not all(key in data for key in required):
        return

    container = {key: data[key] for key in required}

    # Store the node's name
    container["objectName"] = node["name"].value()

    # Store reference to the node object
    container["_tool"] = node

    return container


def update_container(node, keys=dict()):
    """Returns node with updateted containder data

    Arguments:
        node (object): The node in Nuke to imprint as container,
        keys (dict): data which should be updated

    Returns:
        node (object): nuke node with updated container data
    """

    raw_text_data = node['avalon'].value()
    data = toml.loads(raw_text_data, _dict=dict)

    if not isinstance(data, dict):
        return

    # If not all required data return the empty container
    required = ['schema', 'id', 'name',
                'namespace', 'node_name', 'representation']
    if not all(key in data for key in required):
        return

    container = {key: data[key] for key in required}

    for key, value in container.items():
        try:
            container[key] = keys[key]
        except KeyError:
            pass

    node['avalon'].setValue('')
    node['avalon'].setValue(toml.dumps(container))

    return node


def ls():
    """List available containers.

    This function is used by the Container Manager in Nuke. You'll
    need to implement a for-loop that then *yields* one Container at
    a time.

    See the `container.json` schema for details on how it should look,
    and the Maya equivalent, which is in `avalon.maya.pipeline`
    """
    all_nodes = nuke.allNodes(recurseGroups=True)

    # TODO: add readgeo, readcamera, readimage
    reads = [n for n in all_nodes if n.Class() == 'Read']

    for r in reads:
        container = parse_container(r)
        if container:
            yield container


def install(config):
    """Install Nuke-specific functionality of avalon-core.

    This is where you install menus and register families, data
    and loaders into Nuke.

    It is called automatically when installing via `api.install(nuke)`.

    See the Maya equivalent for inspiration on how to implement this.

    """

    _install_menu()
    _register_events()

    pyblish.register_host("nuke")
    # Trigger install on the config's "nuke" package
    try:
        config = importlib.import_module(config.__name__ + ".nuke")
    except ImportError as error:
        log.critical("cannot acces config.nuke: {}".format(error))
        pass
    else:
        if hasattr(config, "install"):
            config.install()
            log.info("config.nuke installed")


def _uninstall_menu():
    menubar = nuke.menu("Nuke")
    menubar.removeItem(api.Session["AVALON_LABEL"])
    self._parent = None


def _install_menu():
    from ..tools import (
        creator,
        # publish,
        workfiles,
        cbloader,
        cbsceneinventory,
        contextmanager
    )
    # for now we are using `lite` version
    # TODO: just for now untill qml in Nuke will be fixed (pyblish-qml#301)
    import pyblish_lite as publish

    # Create menu
    menubar = nuke.menu("Nuke")
    menu = menubar.addMenu(api.Session["AVALON_LABEL"])

    label = "{0}, {1}".format(
        api.Session["AVALON_ASSET"], api.Session["AVALON_TASK"]
    )
    context_menu = menu.addMenu(label)
    context_menu.addCommand("Set Context", contextmanager.show)

    menu.addSeparator()
    menu.addCommand("Work Files...",
                    lambda: workfiles.show(
                        os.environ["AVALON_WORKDIR"]
                    )
                    )
    menu.addSeparator()
    menu.addCommand("Create...", creator.show)
    menu.addCommand("Load...", cbloader.show)
    menu.addCommand("Publish...", publish.show)
    menu.addCommand("Manage...", cbsceneinventory.show)

    menu.addSeparator()

    menu.addCommand("Reset Frame Range", reset_frame_range)
    menu.addCommand("Reset Resolution", reset_resolution)

    menu.addSeparator()
    menu.addCommand("Reload Pipeline", reload_pipeline)

    self._parent = menu


def reset_frame_range():
    """Set frame range to current asset"""

    fps = float(api.Session.get("AVALON_FPS", 25))

    nuke.root()["fps"].setValue(fps)
    log.info(fps)
    asset = api.Session["AVALON_ASSET"]
    asset = io.find_one({"name": asset, "type": "asset"})
    log.info(asset)
    try:
        edit_in = asset["data"]["fstart"]
        edit_out = asset["data"]["fend"]
    except KeyError:
        log.warning(
            "Frame range not set! No edit information found for "
            "\"{0}\".".format(asset["name"])
        )
        return

    nuke.root()["first_frame"].setValue(edit_in)
    nuke.root()["last_frame"].setValue(edit_out)


def reset_resolution():
    """Set resolution to project resolution."""
    project = io.find_one({"type": "project"})
    asset = api.Session["AVALON_ASSET"]
    asset = io.find_one({"name": asset, "type": "asset"})

    try:
        width = asset["data"].get("resolution_width", 1920)
        height = asset["data"].get("resolution_height", 1080)
        pixel_aspect = asset["data"].get("pixel_aspect", 1)

        bbox = asset["data"].get("crop", "0.0.1920.1080")
        if "0.0.1920.1080" in bbox:
            bbox = None

    except KeyError:
        log.warning(
            "No resolution information found for \"{0}\".".format(
                project["name"]
            )
        )
        return

    current_width = nuke.root()["format"].value().width()
    current_height = nuke.root()["format"].value().height()
    current_pixel_aspect = nuke.root()["format"].value().pixelAspect()

    if width != current_width \
            or height != current_height \
            or current_pixel_aspect != pixel_aspect:

        fmt = None
        for f in nuke.formats():
            if f.name() in project["name"]:
                fmt = f

        make_format(
            format=fmt,
            width=int(width),
            height=int(height),
            pixel_aspect=float(pixel_aspect),
            project_name=project["name"]
        )


def make_format(**args):
    if not args["format"]:
        nuke.addFormat(
            "{width} "
            "{height} "
            "0 "
            "0 "
            "{width} "
            "{height} "
            "{pixel_aspect} "
            "{project_name}".format(**args)
        )
        nuke.root()["format"].setValue("{project_name}".format(**args))
    else:
        args["format"].setWidth(args["width"])
        args["format"].setHeight(args["height"])
        args["format"].setX(30)
        args["format"].setY(30)
        args["format"].setR(50)
        args["format"].setT(500)
        args["format"].setPixelAspect(args["pixel_aspect"])
        log.critical("Format `{}` was updated".format(args["format"].name()))


def uninstall():
    """Uninstall all tha was installed

    This is where you undo everything that was done in `install()`.
    That means, removing menus, deregistering families and  data
    and everything. It should be as though `install()` was never run,
    because odds are calling this function means the user is interested
    in re-installing shortly afterwards. If, for example, he has been
    modifying the menu or registered families.

    """
    _uninstall_menu()

    pyblish.deregister_host("nuke")


def publish():
    """Shorthand to publish from within host"""
    import pyblish.util
    return pyblish.util.publish()


def _register_events():

    api.on("taskChanged", _on_task_changed)
    log.info("Installed event callback for 'taskChanged'..")


def _on_task_changed(*args):

    # Update menu
    _uninstall_menu()
    _install_menu()


@contextlib.contextmanager
def viewer_update_and_undo_stop():
    """Lock viewer from updating and stop recording undo steps"""
    try:
        # nuke = getattr(sys.modules["__main__"], "nuke", None)
        # lock all connections between nodes
        # nuke.Root().knob('lock_connections').setValue(1)

        # stop active viewer to update any change
        nuke.activeViewer().stop()
        nuke.Undo.disable()
        yield
    finally:
        # nuke.Root().knob('lock_connections').setValue(0)
        # nuke.activeViewer().start()
        nuke.Undo.enable()
