import os
import sys
import importlib
import logging
from collections import OrderedDict
from __builtin__ import reload

import nuke
from pyblish import api as pyblish

from . import lib, command
from ..lib import find_submodule
from .. import api
from ..vendor.Qt import QtWidgets
from ..pipeline import AVALON_CONTAINER_ID

log = logging.getLogger(__name__)

self = sys.modules[__name__]
self._parent = None  # Main Window cache

AVALON_CONTAINERS = "AVALON_CONTAINERS"
AVALON_CONFIG = os.environ["AVALON_CONFIG"]

USE_OLD_CONTAINER = os.getenv("AVALON_NUKE_OLD_CONTAINER")


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
        reload(module)

    import avalon.nuke
    api.install(avalon.nuke)


def containerise(name,
                 namespace,
                 nodes,
                 context,
                 loader=None,
                 data=None,
                 no_backdrop=True,
                 suffix="CON"):
    """Bundle `node` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        nodes (list): A list of `nuke.Node` object to containerise
        context (dict): Asset information
        loader (str, optional): Name of node used to produce this container.
        data (dict, optional): Additional data to imprint.
        no_backdrop (bool, optional): No container(backdrop) node presented.
        suffix (str, optional): Suffix of container, defaults to `_CON`.

    Returns:
        node (nuke.Node): containerised nuke's node object

    """
    from nukescripts import autoBackdrop

    if isinstance(name, nuke.Node):
        # For compatibling with old style args
        #   containerise(node, name, namespace, context, ...)
        _ = nodes
        nodes = [name]
        name = namespace
        namespace = _

    data = OrderedDict(
        [
            ("schema", "avalon-core:container-2.0"),
            ("id", AVALON_CONTAINER_ID),
            ("name", name),
            ("namespace", namespace),
            ("loader", str(loader)),
            ("representation", str(context["representation"]["_id"])),
        ],

        **data or dict()
    )

    if USE_OLD_CONTAINER:
        node = nodes[0]
        lib.set_avalon_knob_data(node, data)
        return node

    # New style

    container_color = data.pop("color", int("0x7A7A7AFF", 16))
    container_name = "%s_%s_%s" % (namespace, name, suffix)

    lib.reset_selection()
    lib.select_nodes(nodes)

    container = autoBackdrop()
    container.setName(container_name)
    container["label"].setValue(container_name)
    container["tile_color"].setValue(container_color)
    container["selected"].setValue(True)
    # (NOTE) Backdrop may not fully cover if there's only one node, so we
    #        expand backdrop a bit ot ensure that.
    container["bdwidth"].setValue(container["bdwidth"].value() + 100)
    container["bdheight"].setValue(container["bdheight"].value() + 100)
    container["xpos"].setValue(container["xpos"].value() - 50)

    lib.set_avalon_knob_data(container, data)

    container_id = lib.set_id(container)
    for node in nodes:
        lib.set_id(node, container_id=container_id)

    # Containerising

    nuke.nodeCopy("_containerizing_")

    main_container = nuke.toNode(AVALON_CONTAINERS)
    if main_container is None:
        main_container = nuke.createNode("Group")
        main_container.setName(AVALON_CONTAINERS)
        main_container["postage_stamp"].setValue(True)
        main_container["note_font_size"].setValue(40)
        main_container["tile_color"].setValue(int("0x283648FF", 16))
        main_container["xpos"].setValue(-500)
        main_container["ypos"].setValue(-500)

    main_container.begin()
    nuke.nodePaste("_containerizing_")
    main_container.end()

    if no_backdrop:
        nuke.delete(container)

    return container


def parse_container(node):
    """Returns containerised data of a node

    Reads the imprinted data from `containerise`.

    Arguments:
        node (nuke.Node): Nuke's node object to read imprinted data

    Returns:
        dict: The container schema data for this container node.

    """
    data = lib.get_avalon_knob_data(node)

    # Store the node's name
    data["objectName"] = node["name"].value()
    # Store reference to the node object
    data["_node"] = node
    # Get containerized nodes
    if node.fullName() == "%s.%s" % (AVALON_CONTAINERS, node.name()):
        data["_members"] = lib.lsattr("avalon:containerId",
                                      value=data["avalonId"],
                                      group=nuke.toNode(AVALON_CONTAINERS),
                                      recursive=True)

    return data


def update_container(node, keys=None):
    """Returns node with updateted containder data

    Arguments:
        node (nuke.Node): The node in Nuke to imprint as container,
        keys (dict, optional): data which should be updated

    Returns:
        node (nuke.Node): nuke node with updated container data

    Raises:
        TypeError on given an invalid container node

    """
    keys = keys or dict()

    container = parse_container(node)
    if not container:
        raise TypeError("Not a valid container node.")

    # Remove unprintable entries
    container.pop("_node", None)
    container.pop("_members", None)

    container.update(keys)
    node = lib.set_avalon_knob_data(node, container)

    return node


class Creator(api.Creator):
    """Creator class wrapper
    """
    node_color = "0xdfea5dff"

    def process(self):
        from nukescripts import autoBackdrop

        instance = None

        if (self.options or {}).get("useSelection"):

            nodes = nuke.selectedNodes()
            if not nodes:
                nuke.message("Please select nodes that you "
                             "wish to add to a container")
                return

            elif len(nodes) == 1:
                # only one node is selected
                instance = nodes[0]

        if not instance:
            # Not using selection or multiple nodes selected
            bckd_node = autoBackdrop()
            bckd_node["tile_color"].setValue(int(self.node_color, 16))
            bckd_node["note_font_size"].setValue(24)
            bckd_node["label"].setValue("[{}]".format(self.name))

            instance = bckd_node

        # add avalon knobs
        lib.set_avalon_knob_data(instance, self.data)
        lib.add_publish_knob(instance)

        return instance


def _ls1():
    """Yields all nodes for listing Avalon containers"""
    for node in nuke.allNodes(recurseGroups=False):
        yield node


def _ls2():
    """Yields nodes that has 'avalon:id' knob from AVALON_CONTAINERS"""
    for node in nuke.allNodes("BackdropNode",
                              group=nuke.toNode(AVALON_CONTAINERS)):
        knob = node.fullName() + ".avalon:id"
        if nuke.exists(knob) and nuke.knob(knob) == AVALON_CONTAINER_ID:
            yield node


_ls = _ls1 if USE_OLD_CONTAINER else _ls2


def ls():
    """List available containers.

    This function is used by the Container Manager in Nuke. You'll
    need to implement a for-loop that then *yields* one Container at
    a time.

    See the `container.json` schema for details on how it should look,
    and the Maya equivalent, which is in `avalon.maya.pipeline`
    """
    config_host = find_submodule(api.registered_config(), "nuke")
    has_metadata_collector = hasattr(config_host, "collect_container_metadata")

    container_nodes = _ls()

    for container in container_nodes:
        data = parse_container(container)
        if data is None:
            continue

        # Collect custom data if attribute is present
        if has_metadata_collector:
            metadata = config_host.collect_container_metadata(container)
            data.update(metadata)

        yield data


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

    log.info("config.nuke installed")


def get_main_window():
    """Acquire Nuke's main window"""
    if self._parent is None:
        top_widgets = QtWidgets.QApplication.topLevelWidgets()
        name = "Foundry::UI::DockMainWindow"
        main_window = next(widget for widget in top_widgets if
                           widget.inherits("QMainWindow") and
                           widget.metaObject().className() == name)
        self._parent = main_window
    return self._parent


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
    )

    # Create menu
    menubar = nuke.menu("Nuke")
    menu = menubar.addMenu(api.Session["AVALON_LABEL"])

    _add_contextmanager_menu(menu)

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
                        os.environ["AVALON_WORKDIR"],
                        parent=get_main_window())
                    )

    menu.addSeparator()
    menu.addCommand("Reset Frame Range", command.reset_frame_range)
    menu.addCommand("Reset Resolution", command.reset_resolution)

    # add reload pipeline only in debug mode
    if bool(os.getenv("NUKE_DEBUG")):
        menu.addSeparator()
        menu.addCommand("Reload Pipeline", reload_pipeline)


def _uninstall_menu():
    """Uninstalling Avalon menu to Nuke
    """
    menubar = nuke.menu("Nuke")
    menubar.removeItem(api.Session["AVALON_LABEL"])


def _add_contextmanager_menu(menu):
    label = "{0}, {1}".format(
        api.Session["AVALON_ASSET"], api.Session["AVALON_TASK"]
    )
    context_action = menu.addCommand(label)
    context_action.setEnabled(False)


def _update_menu_task_label():
    menubar = nuke.menu("Nuke")
    menu = menubar.findItem(api.Session["AVALON_LABEL"])

    menu.removeItem(menu.items()[0].name())  # Assume it is the first item
    _add_contextmanager_menu(menu)


def publish():
    """Shorthand to publish from within host"""
    import pyblish.util
    return pyblish.util.publish()


def _register_events():

    api.on("taskChanged", _on_task_changed)
    log.info("Installed event callback for 'taskChanged'..")


def _on_task_changed(*args):

    # Update menu
    _update_menu_task_label()


# Backwards compatibility
reset_frame_range_handles = command.reset_frame_range
get_handles = command.get_handles
reset_resolution = command.reset_resolution
viewer_update_and_undo_stop = command.viewer_update_and_undo_stop
