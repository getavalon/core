import os
import logging
import contextlib
import importlib
from collections import OrderedDict
from __builtin__ import reload

from pyblish import api as pyblish
from ..pipeline import AVALON_CONTAINER_ID
from .. import api, io, schema
from . import lib
import nuke

log = logging.getLogger(__name__)

AVALON_CONFIG = os.environ["AVALON_CONFIG"]


def reload_pipeline():
    """Attempt to reload pipeline at run-time.

    CAUTION: This is primarily for development and debugging purposes.

    """

    api.uninstall()
    _uninstall_menu()

    for module in ("avalon.api",
                   "avalon.io",
                   "avalon.lib",
                   "avalon.pipeline",
                   "avalon.tools",
                   "avalon.nuke",
                   "avalon.nuke.pipeline",
                   "avalon.nuke.lib",
                   "avalon.nuke.workio"
                   ):

        log.info("Reloading module: {}...".format(module))

        module = importlib.import_module(module)

        try:
            importlib.reload(module)
        except AttributeError as e:
            log.warning("Cannot reload module: {}".format(e))
            reload(module)

    import avalon.nuke
    api.install(avalon.nuke)

    _register_events()


def containerise(node,
                 name,
                 namespace,
                 context,
                 loader=None,
                 data=None):
    """Bundle `node` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        node (obj): Nuke's node object to imprint as container,
                    usually a Reader.
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        context (dict): Asset information
        loader (str, optional): Name of node used to produce this container.

    Returns:
        node (obj): containerised nuke's node object

    """

    data_imprint = OrderedDict({
        "schema": "avalon-core:container-2.0",
        "id": AVALON_CONTAINER_ID,
        "name": str(name),
        "namespace": str(namespace),
        "loader": str(loader),
        "representation": str(context["representation"]["_id"]),
    })

    if data:
        {data_imprint.update({k: v}) for k, v in data.items()}

    log.debug("Data for Imprint: {}".format(data_imprint))

    lib.set_avalon_knob_data(node, data_imprint)

    return node


def parse_container(node, validate=True):
    """Returns containerised data of a node

    Reads the imprinted data from `containerise`.

    Arguments:
        node (obj): Nuke's node object to read imprinted data

    Returns:
        container (dict): imprinted container data
    """
    data = lib.get_avalon_knob_data(node)

    if validate and data and data.get("schema"):
        schema.validate(data)

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
    container["_node"] = node

    return container


def update_container(node, keys=dict()):
    """Returns node with updateted containder data

    Arguments:
        node (object): The node in Nuke to imprint as container,
        keys (dict): data which should be updated

    Returns:
        node (object): nuke node with updated container data
    """

    data = lib.get_avalon_knob_data(node)

    container = dict()
    container = {key: data[key] for key in data}

    for key, value in container.items():
        try:
            container[key] = keys[key]
        except KeyError:
            pass

    node = lib.set_avalon_knob_data(node, container)

    return node


class Creator(api.Creator):
    """Creator class wrapper
    """
    node_color = "0xdfea5dff"

    def __init__(self, *args, **kwargs):
        super(Creator, self).__init__(*args, **kwargs)
        # make sure no duplicity of subsets are in workfile
        if lib.check_subsetname_exists(
                nuke.allNodes(),
                self.data["subset"]):
            msg = "The subset name `{0}` is already used on a node in" \
                  "this workfile.".format(self.data["subset"])
            self.log.error(msg + '\n\nPlease use other subset name!')
            raise NameError("`{0}: {1}".format(__name__, msg))
        return

    def process(self):
        from nukescripts import autoBackdrop
        nodes = list()
        if (self.options or {}).get("useSelection"):
            nodes = nuke.selectedNodes()

            if len(nodes) == 1:
                # only one node is selected
                node = nodes[0]
                instance = lib.imprint(node, self.data)
                return instance

            elif len(nodes) >= 2:
                bckd_node = autoBackdrop()
                bckd_node["name"].setValue("{}_BDN".format(self.name))
                bckd_node["tile_color"].setValue(int(self.node_color, 16))
                bckd_node["note_font_size"].setValue(24)
                bckd_node["label"].setValue("[{}]".format(self.name))
                # add avalon knobs
                instance = lib.imprint(bckd_node, self.data)

                return instance
            else:
                nuke.message("Please select nodes you "
                             "wish to add to a container")
                return
        else:
            bckd_node = autoBackdrop()
            bckd_node["name"].setValue("{}_BDN".format(self.name))
            bckd_node["tile_color"].setValue(int(self.node_color, 16))
            bckd_node["note_font_size"].setValue(24)
            bckd_node["label"].setValue("[{}]".format(self.name))
            # add avalon knobs
            instance = lib.imprint(bckd_node, self.data)

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

    nodes = [n for n in all_nodes]

    for n in nodes:
        log.debug("name: `{}`".format(n.name()))
        container = parse_container(n)
        if container:
            yield container


def install():
    """Install Nuke-specific functionality of avalon-core.

    This is where you install menus and register families, data
    and loaders into Nuke.

    It is called automatically when installing via `api.install(nuke)`.

    See the Maya equivalent for inspiration on how to implement this.

    """

    _install_menu()
    _register_events()

    pyblish.register_host("nuke")


def uninstall():
    """Uninstall all that was previously installed

    This is where you undo everything that was done in `install()`.
    That means, removing menus, deregistering families and  data
    and everything. It should be as though `install()` was never run,
    because odds are calling this function means the user is interested
    in re-installing shortly afterwards. If, for example, he has been
    modifying the menu or registered families.

    """

    _uninstall_menu()

    pyblish.deregister_host("nuke")


def _install_menu():
    """Installing Avalon menu to Nuke
    """
    from ..tools import (
        creator,
        publish,
        workfiles,
        loader,
        sceneinventory,
        libraryloader
    )

    # Create menu
    menubar = nuke.menu("Nuke")
    menu = menubar.addMenu(api.Session["AVALON_LABEL"])

    label = "{0}, {1}".format(
        api.Session["AVALON_ASSET"], api.Session["AVALON_TASK"]
    )
    context_action = menu.addCommand(label)
    context_action.setEnabled(False)

    menu.addSeparator()
    menu.addCommand("Create...",
                    lambda: creator.show(parent=get_main_window()))
    menu.addCommand("Load...",
                    lambda: loader.show(parent=get_main_window(),
                                        use_context=True))
    menu.addCommand("Publish...",
                    lambda: publish.show(parent=get_main_window()))
    menu.addCommand("Manage...",
                    lambda: sceneinventory.show(parent=get_main_window()))

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
        loader.show(use_context=True)
    )
    menu.addCommand("Publish...", publish.show)
    menu.addCommand("Manage...", sceneinventory.show)
    menu.addCommand("Library...", libraryloader.show)

    menu.addSeparator()
    menu.addCommand("Reset Frame Range", reset_frame_range_handles)
    menu.addCommand("Reset Resolution", reset_resolution)

    # add reload pipeline only in debug mode
    if bool(os.getenv("NUKE_DEBUG")):
        menu.addSeparator()
        menu.addCommand("Reload Pipeline", reload_pipeline)


def _uninstall_menu():
    """Uninstalling Avalon menu to Nuke
    """
    menubar = nuke.menu("Nuke")
    menubar.removeItem(api.Session["AVALON_LABEL"])


def reset_frame_range_handles():
    """ Set frame range to current asset
        Also it will set a Viewer range with
        displayed handles
    """

    fps = float(api.Session.get("AVALON_FPS", 25))

    nuke.root()["fps"].setValue(fps)
    name = api.Session["AVALON_ASSET"]
    asset = io.find_one({"name": name, "type": "asset"})
    asset_data = asset["data"]

    handles = get_handles(asset)

    frame_start = int(asset_data.get(
        "frameStart",
        asset_data.get("edit_in")))

    frame_end = int(asset_data.get(
        "frameEnd",
        asset_data.get("edit_out")))

    if not all([frame_start, frame_end]):
        missing = ", ".join(["frame_start", "frame_end"])
        msg = "'{}' are not set for asset '{}'!".format(missing, name)
        log.warning(msg)
        nuke.message(msg)
        return

    frame_start -= handles
    frame_end += handles

    nuke.root()["first_frame"].setValue(frame_start)
    nuke.root()["last_frame"].setValue(frame_end)

    # setting active viewers
    vv = nuke.activeViewer().node()
    vv['frame_range_lock'].setValue(True)
    vv['frame_range'].setValue('{0}-{1}'.format(
        int(asset_data["frameStart"]),
        int(asset_data["frameEnd"]))
    )


def get_handles(asset):
    """ Gets handles data

    Arguments:
        asset (dict): avalon asset entity

    Returns:
        handles (int)
    """
    data = asset["data"]
    if "handles" in data and data["handles"] is not None:
        return int(data["handles"])

    parent_asset = None
    if "visualParent" in data:
        vp = data["visualParent"]
        if vp is not None:
            parent_asset = io.find_one({"_id": io.ObjectId(vp)})

    if parent_asset is None:
        parent_asset = io.find_one({"_id": io.ObjectId(asset['parent'])})

    if parent_asset is not None:
        return get_handles(parent_asset)
    else:
        return 0


def reset_resolution():
    """Set resolution to project resolution."""
    project = io.find_one({"type": "project"})
    p_data = project["data"]

    width = p_data.get("resolution_width",
                       p_data.get("resolutionWidth"))
    height = p_data.get("resolution_height",
                        p_data.get("resolutionHeight"))

    if not all([width, height]):
        missing = ", ".join(["width", "height"])
        msg = "No resolution information `{0}` found for '{1}'.".format(
            missing,
            project["name"])
        log.warning(msg)
        nuke.message(msg)
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
        viewer = nuke.activeViewer()
        if viewer:
            viewer.stop()
        else:
            log.warning("No available active Viewer")
        nuke.Undo.disable()
        yield
    finally:
        nuke.Undo.enable()
