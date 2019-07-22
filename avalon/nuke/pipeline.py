import os
import sys
from collections import OrderedDict
from bson.objectid import ObjectId
import importlib
from .. import api, io
import contextlib
from pyblish import api as pyblish
from ..vendor import toml
import logging
import nuke
from . import lib


log = logging.getLogger(__name__)

AVALON_CONFIG = os.environ["AVALON_CONFIG"]


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
                   "avalon.nuke.pipeline",
                   "avalon.nuke.lib",
                   "avalon.tools.cbloader.app",
                   "avalon.tools.creator.app",
                   "avalon.tools.manager.app",
                   "avalon.tools.libraryloader",

                   "avalon.api",
                   "avalon.tools",
                   "avalon.nuke",
                   "{}".format(AVALON_CONFIG),
                   "{}.lib".format(AVALON_CONFIG)):
        log.info("Reloading module: {}...".format(module))
        module = importlib.import_module(module)
        reload(module)

    import avalon.nuke
    api.install(avalon.nuke)

    _install_menu()
    _register_events()


def set_avalon_knob_data(node, data):
    """ Sets a data into nodes's avalon knob

    Arguments:
        node (object): The node in Nuke to imprint as data,
        data (dict): data to be printed into Avalon knob

    Returns:
        True (bool)
    """
    try:
        lib.add_avalon_tab_knob(node)
        lib.add_avalon_tab_knob(node)

        node['avalon'].setValue(toml.dumps(data))

        return True
    except Exception as e:
        log.warning("set_avalon_knob_data: `{}`".format(e))
        return False


def get_avalon_knob_data(node):
    """ Gets all imprinted data from nodes's avalon knob

    Arguments:
        node (object): The node in Nuke to read data from,

    Returns:
        data (dict): imprinted data
    """
    try:
        raw_text_data = node['avalon'].value()
    except Exception as e:
        log.debug("Creating avalon knob: `{}`".format(e))
        lib.add_avalon_tab_knob(node)
        return get_avalon_knob_data(node)

    data = toml.loads(raw_text_data, _dict=dict)
    return data


def containerise(node,
                 name,
                 namespace,
                 context,
                 loader=None,
                 data=None):
    """Bundle `nodes` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        node (object): The node in Nuke to imprint as container,
        usually a Reader.
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        context (dict): Asset information
        loader (str, optional): Name of node used to produce this container.

    Returns:
        None

    """

    data_imprint = OrderedDict({
        "schema": "avalon-core:container-2.0",
        "id": "pyblish.avalon.container",
        "name": str(name),
        "namespace": str(namespace),
        "loader": str(loader),
        "representation": str(context["representation"]["_id"]),
    })

    if data:
        {data_imprint.update({k: v}) for k, v in data.items()}

    log.info("data_imprint: {}".format(data_imprint))

    set_avalon_knob_data(node, data_imprint)


def parse_container(node):
    """Returns containerised data of a node

    This reads the imprinted data from `containerise`.

    """
    data = get_avalon_knob_data(node)

    if not isinstance(data, dict):
        return

    # If not all required data return the empty container
    required = ['schema', 'id', 'name',
                'namespace', 'loader', 'representation']
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
                'namespace', 'objectName', 'representation', 'version']
    container = dict()

    # check if key in data
    for k in required:
        if not data.get(k, 0):
            # if not then create the key in container and data
            data[k] = 0

    container = {key: data[key] for key in data}

    for key, value in container.items():
        try:
            container[key] = keys[key]
        except KeyError:
            pass

    node['avalon'].setValue('')
    node['avalon'].setValue(toml.dumps(container))

    return node


class Creator(api.Creator):
    def process(self):
        nodes = nuke.allNodes()

        if (self.options or {}).get("useSelection"):
            nodes = nuke.selectedNodes()

        instance = [n for n in nodes
                    if n["name"].value() in self.name] or None

        instance = lib.imprint(instance, self.data)

        return instance


def ls():
    """List available containers.

    This function is used by the Container Manager in Nuke. You'll
    need to implement a for-loop that then *yields* one Container at
    a time.

    See the `container.json` schema for details on how it should look,
    and the Maya equivalent, which is in `avalon.maya.pipeline`
    """
    all_nodes = nuke.allNodes(recurseGroups=False)

    # TODO: add readgeo, readcamera, readimage
    nodes = [n for n in all_nodes]

    for n in nodes:
        log.info("__ name node ls: `{}`".format(n.name()))
        container = parse_container(n)
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
    config = find_host_config(config)

    if hasattr(config, "install"):
        config.install()

    log.info("config.nuke installed")


def find_host_config(config):
    try:
        config = importlib.import_module(config.__name__ + ".nuke")
    except ImportError as exc:
        if str(exc) != "No module name {}".format(config.__name__ + ".nuke"):
            raise
        config = None

    return config


def uninstall(config):
    """Uninstall all tha was installed

    This is where you undo everything that was done in `install()`.
    That means, removing menus, deregistering families and  data
    and everything. It should be as though `install()` was never run,
    because odds are calling this function means the user is interested
    in re-installing shortly afterwards. If, for example, he has been
    modifying the menu or registered families.

    """
    config = find_host_config(config)
    if hasattr(config, "uninstall"):
        config.uninstall()

    _uninstall_menu()

    pyblish.deregister_host("nuke")


def _install_menu():
    from ..tools import (
        creator,
        publish,
        workfiles,
        cbloader,
        cbsceneinventory,
        contextmanager,
        libraryloader
    )

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
    menu.addCommand(
        "Load...", command=lambda *args:
        cbloader.show(use_context=True)
    )
    menu.addCommand("Publish...", publish.show)
    menu.addCommand("Manage...", cbsceneinventory.show)
    menu.addCommand("Library...", libraryloader.show)

    menu.addSeparator()
    menu.addCommand("Reset Frame Range", reset_frame_range_handles)
    menu.addCommand("Reset Resolution", reset_resolution)

    menu.addSeparator()
    menu.addCommand("Reload Pipeline", reload_pipeline)


def _uninstall_menu():
    menubar = nuke.menu("Nuke")
    menubar.removeItem(api.Session["AVALON_LABEL"])


def reset_frame_range():
    """Set frame range to current asset"""

    fps = float(api.Session.get("AVALON_FPS", 25))

    nuke.root()["fps"].setValue(fps)
    asset = api.Session["AVALON_ASSET"]
    asset = io.find_one({"name": asset, "type": "asset"})

    try:
        edit_in = int(asset["data"]["fstart"])
        edit_out = int(asset["data"]["fend"])
    except KeyError:
        log.warning(
            "Frame range not set! No edit information found for "
            "\"{0}\".".format(asset["name"])
        )
        return

    nuke.root()["first_frame"].setValue(edit_in)
    nuke.root()["last_frame"].setValue(edit_out)


def reset_frame_range_handles():
    """Set frame range to current asset"""

    fps = float(api.Session.get("AVALON_FPS", 25))

    nuke.root()["fps"].setValue(fps)
    name = api.Session["AVALON_ASSET"]
    asset = io.find_one({"name": name, "type": "asset"})

    if "data" not in asset:
        msg = "Asset {} don't have set any 'data'".format(name)
        log.warning(msg)
        nuke.message(msg)
        return
    data = asset["data"]

    missing_cols = []
    check_cols = ["fstart", "fend"]

    for col in check_cols:
        if col not in data:
            missing_cols.append(col)

    if len(missing_cols) > 0:
        missing = ", ".join(missing_cols)
        msg = "'{}' are not set for asset '{}'!".format(missing, name)
        log.warning(msg)
        nuke.message(msg)
        return

    handles = get_handles(asset)
    edit_in = int(asset["data"]["fstart"]) - handles
    edit_out = int(asset["data"]["fend"]) + handles

    nuke.root()["first_frame"].setValue(edit_in)
    nuke.root()["last_frame"].setValue(edit_out)

    # setting active viewers
    vv = nuke.activeViewer().node()
    vv['frame_range_lock'].setValue(True)
    vv['frame_range'].setValue('{0}-{1}'.format(
        int(asset["data"]["fstart"]),
        int(asset["data"]["fend"]))
    )



def get_handles(asset):
    data = asset["data"]
    if "handles" in data and data["handles"] is not None:
        return int(data["handles"])

    parent_asset = None
    if "visualParent" in data:
        vp = data["visualParent"]
        if vp is not None:
            parent_asset = io.find_one({"_id": ObjectId(vp)})

    if parent_asset is None:
        parent_asset = io.find_one({"_id": ObjectId(asset['parent'])})

    if parent_asset is not None:
        return get_handles(parent_asset)
    else:
        return 0


def reset_resolution():
    """Set resolution to project resolution."""
    project = io.find_one({"type": "project"})

    try:
        width = project["data"].get("resolution_width", 1920)
        height = project["data"].get("resolution_height", 1080)
    except KeyError:
        print(
            "No resolution information found for \"{0}\".".format(
                project["name"]
            )
        )
        return

    current_width = nuke.root()["format"].value().width()
    current_height = nuke.root()["format"].value().height()

    if width != current_width or height != current_height:

        fmt = None
        for f in nuke.formats():
            if f.width() == width and f.height() == height:
                fmt = f.name()

        if not fmt:
            nuke.addFormat(
                "{0} {1} {2}".format(int(width), int(height), project["name"])
            )
            fmt = project["name"]

        nuke.root()["format"].setValue(fmt)


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
        # stop active viewer to update any change
        try:
            nuke.activeViewer().stop()
        except Exception as e:
            log.warning("No available active Viewer: `{}`".format(e))
        nuke.Undo.disable()
        yield
    finally:
        # nuke.Root().knob('lock_connections').setValue(0)
        # nuke.activeViewer().start()
        nuke.Undo.enable()
