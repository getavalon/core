import os
import logging
import contextlib
import importlib
from collections import OrderedDict
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

    import importlib

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
        importlib.reload(module)

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

    if validate:
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

    def process(self):
        import nukescripts
        nodes = list()
        if (self.options or {}).get("useSelection"):
            nodes = nuke.selectedNodes()

            if len(nodes) == 1:
                # only one node is selected
                node = nodes[0]
                instance = lib.imprint(node, self.data)
                return instance

            elif len(nodes) >= 2:
                # if more nodes selected
                output_node = None
                input_node = None

                # get original output connection
                connected_to_output = list()
                for n in nodes:
                    dep_nodes = n.dependent()
                    if dep_nodes is []:
                        continue
                    for dep_n in dep_nodes:
                        if dep_n.name() not in [n.name() for n in nodes]:
                            connected_to_output.append(
                                nuke.toNode(dep_n.name()))
                    if connected_to_output:
                        output_node = n.name()

                # get original input connection
                inputs = dict()
                for n in nodes:
                    connected_to_inputs = list()
                    ln_n = n.input(0)
                    if not ln_n:
                        continue
                    if ln_n.name() not in [n.name() for n in nodes]:
                        connected_to_inputs.append(
                            nuke.toNode(ln_n.name()))
                    if connected_to_inputs:
                        inputs[n.name()] = connected_to_inputs

                nuke.nodeCopy('%clipboard%')
                nukescripts.misc.clear_selection_recursive()

                # more nodes are sellected
                # jump back from group if we are in any
                nuke.endGroup()

                # create group node as container for selected nodes
                GN = nuke.createNode("Group")
                GN["name"].setValue(self.name)

                # adding content to the group node
                with GN:
                    nuke.nodePaste('%clipboard%')
                    nodes_pasted = [n.name() for n in nuke.selectedNodes()]

                    # input nodes solver (multiple input nodes)
                    grp_inputs_lnk = dict()
                    input_index = 0
                    for i_node_name, inputs in inputs.items():
                        input_node_name = "{}_input".format(i_node_name)
                        now_node = nuke.toNode(i_node_name)
                        input_node = nuke.createNode(
                            "Input",
                            input_node_name)
                        now_node.setInput(0, input_node)
                        grp_inputs_lnk[input_index] = inputs
                        input_index += 1

                    # out  put node solver (single output node)
                    if output_node:
                        last_node = nuke.toNode(output_node)
                        out_node = nuke.createNode(
                            "Output",
                            "Output1")
                        out_node.setInput(0, last_node)


                # delete the originally selected nodes
                for n in nodes:
                    nuke.delete(n)

                # connect group to inputs
                # list with connected nodes
                # list with group inputs
                connected_to_inputs
                input_node # name of node

                # connect group to ouptut
                # list with connected outputs
                connected_to_output
                output_node

                # add avalon knobs
                instance = lib.imprint(GN, self.data)

                return instance
            else:
                nuke.message("Please select only one node")
                return


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
        if str(exc) != "No module named {}".format("nuke"):
            raise
        config = None

    return config


def uninstall(config):
    """Uninstall all that was previously installed

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
    """Installing Avalon menu to Nuke
    """
    from ..tools import (
        creator,
        publish,
        workfiles,
        loader,
        sceneinventory,
        contextmanager
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
        loader.show(use_context=True)
    )
    menu.addCommand("Publish...", publish.show)
    menu.addCommand("Manage...", sceneinventory.show)

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
