# Standard library
import sys
import importlib

# Pyblish libraries
import pyblish.api

# Host libraries
import hou

# Local libraries
from . import lib
from ..lib import logger
from avalon import api, schema

from ..pipeline import AVALON_CONTAINER_ID

self = sys.modules[__name__]
self._has_been_setup = False
self._parent = None
self._events = dict()

AVALON_CONTAINERS = "/obj/AVALON_CONTAINERS"
IS_HEADLESS = not hasattr(hou, "ui")


def install(config):
    """Setup integration
    Register plug-ins and integrate into the host

    """

    print("Registering callbacks")
    _register_callbacks()

    pyblish.api.register_host("houdini")
    pyblish.api.register_host("hython")
    pyblish.api.register_host("hpython")

    self._has_been_setup = True

    config = find_host_config(config)
    if hasattr(config, "install"):
        config.install()


def uninstall(config):
    """Uninstall Houdini-specific functionality of avalon-core.

    This function is called automatically on calling `api.uninstall()`.

    Args:
        config: configuration module

    """

    config = find_host_config(config)
    if hasattr(config, "uninstall"):
        config.uninstall()

    pyblish.api.deregister_host("hython")
    pyblish.api.deregister_host("hpython")
    pyblish.api.deregister_host("houdini")


def find_host_config(config):
    config_name = config.__name__
    try:
        config = importlib.import_module(config_name + ".houdini")
    except ImportError as exc:
        if str(exc) != "No module name {}".format(config_name + ".houdini"):
            raise
        config = None

    return config


def reload_pipeline(*args):
    """Attempt to reload pipeline at run-time.

    CAUTION: This is primarily for development and debugging purposes.

    """

    import importlib

    api.uninstall()

    for module in ("avalon.io",
                   "avalon.lib",
                   "avalon.pipeline",

                   "avalon.houdini.pipeline",
                   "avalon.houdini.lib",
                   "avalon.tools.creator.app",

                   # NOTE(marcus): These have circular depenendencies
                   #               that is preventing reloadability
                   # "avalon.tools.loader.delegates",
                   # "avalon.tools.loader.model",
                   # "avalon.tools.loader.widgets",
                   # "avalon.tools.loader.app",
                   # "avalon.tools.sceneinventory.model",
                   # "avalon.tools.sceneinventory.proxy",
                   # "avalon.tools.sceneinventory.app",
                   # "avalon.tools.projectmanager.dialogs",
                   # "avalon.tools.projectmanager.lib",
                   # "avalon.tools.projectmanager.model",
                   # "avalon.tools.projectmanager.style",
                   # "avalon.tools.projectmanager.widget",
                   # "avalon.tools.projectmanager.app",

                   "avalon.api",
                   "avalon.tools",
                   "avalon.houdini"):
        module = importlib.import_module(module)
        reload(module)

    self._parent = {hou.ui.mainQtWindow().objectName(): hou.ui.mainQtWindow()}

    import avalon.houdini
    api.install(avalon.houdini)


def _discover_gui():
    """Return the most desirable of the currently registered GUIs"""

    # Prefer last registered
    guis = reversed(pyblish.api.registered_guis())

    for gui in guis:
        try:
            gui = __import__(gui).show
        except (ImportError, AttributeError):
            continue
        else:
            return gui


def teardown():
    """Remove integration"""
    if not self._has_been_setup:
        return

    self._has_been_setup = False
    print("pyblish: Integration torn down successfully")


def containerise(name,
                 namespace,
                 nodes,
                 context,
                 loader=None,
                 suffix=""):
    """Bundle `nodes` into a subnet and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        nodes (list): Long names of nodes to containerise
        context (dict): Asset information
        loader (str, optional): Name of loader used to produce this container.
        suffix (str, optional): Suffix of container, defaults to `_CON`.

    Returns:
        container (str): Name of container assembly

    """

    # Ensure AVALON_CONTAINERS subnet exists
    subnet = hou.node(AVALON_CONTAINERS)
    if subnet is None:
        obj_network = hou.node("/obj")
        subnet = obj_network.createNode("subnet",
                                        node_name="AVALON_CONTAINERS")

    # Create proper container name
    container_name = "{}_{}".format(name, suffix or "CON")
    container = hou.node("/obj/{}".format(name))
    container.setName(container_name)

    data = {
        "schema": "avalon-core:container-2.0",
        "id": AVALON_CONTAINER_ID,
        "name": name,
        "namespace": namespace,
        "loader": str(loader),
        "representation": str(context["representation"]["_id"]),
    }

    lib.imprint(container, data)

    # "Parent" the container under the container network
    hou.moveNodesTo([container], subnet)

    subnet.node(container_name).moveToGoodPosition()

    return container


def parse_container(container, validate=True):
    """Return the container node's full container data.

    Args:
        container (hou.Node): A container node name.
        validate(bool): turn the validation for the container on or off

    Returns:
        dict: The container schema data for this container node.

    """
    data = lib.read(container)

    # Backwards compatibility pre-schemas for containers
    data["schema"] = data.get("schema", "avalon-core:container-1.0")

    # Append transient data
    data["objectName"] = container.path()
    data["node"] = container

    if validate:
        schema.validate(data)

    return data


def ls():
    containers = []
    for identifier in (AVALON_CONTAINER_ID,
                       "pyblish.mindbender.container"):
        containers += lib.lsattr("id", identifier)

    for container in sorted(containers):
        data = parse_container(container)

        # Collect custom data if attribute is present
        config = find_host_config(api.registered_config())
        if hasattr(config, "collect_container_metadata"):
            metadata = config.collect_container_metadata(container)
            data.update(metadata)

        yield data


class Creator(api.Creator):
    """Creator plugin to create instances in Houdini

    To support the wide range of node types for render output (Alembic, VDB,
    Mantra) the Creator needs a node type to create the correct instance

    By default, if none is given, is `geometry`. An example of accepted node
    types: geometry, alembic, ifd (mantra)

    Please check the Houdini documentation for more node types.

    Tip: to find the exact node type to create press the `i` left of the node
    when hovering over a node. The information is visible under the name of
    the node.

    """

    def __init__(self, *args, **kwargs):
        super(Creator, self).__init__(*args, **kwargs)
        self.nodes = list()

    def process(self):
        """This is the base functionality to create instances in Houdini

        The selected nodes are stored in self to be used in an override method.
        This is currently necessary in order to support the multiple output
        types in Houdini which can only be rendered through their own node.

        Default node type if none is given is `geometry`

        It also makes it easier to apply custom settings per instance type

        Example of override method for Alembic:

            def process(self):
                instance =  super(CreateEpicNode, self, process()
                # Set paramaters for Alembic node
                instance.setParms(
                    {"sop_path": "$HIP/%s.abc" % self.nodes[0]}
                )

        Returns:
            hou.Node

        """

        if (self.options or {}).get("useSelection"):
            self.nodes = hou.selectedNodes()

        # Get the node type and remove it from the data, not needed
        node_type = self.data.pop("node_type", None)
        if node_type is None:
            node_type = "geometry"

        # Get out node
        out = hou.node("/out")
        instance = out.createNode(node_type, node_name=self.name)
        instance.moveToGoodPosition()

        lib.imprint(instance, self.data)

        return instance


def on_file_event_callback(event):
    if event == hou.hipFileEventType.AfterLoad:
        api.emit("open", [event])
    elif event == hou.hipFileEventType.AfterSave:
        api.emit("save", [event])
    elif event == hou.hipFileEventType.BeforeSave:
        api.emit("before_save", [event])
    elif event == hou.hipFileEventType.AfterClear:
        api.emit("new", [event])


def on_houdini_initialize():

    main_window = hou.qt.mainWindow()
    self._parent = {main_window.objectName(): main_window}


def _register_callbacks():

    for handler, event in self._events.copy().items():
        if event is None:
            continue

        try:
            hou.hipFile.removeEventCallback(event)
        except RuntimeError as e:
            logger.info(e)

    self._events[on_file_event_callback] = hou.hipFile.addEventCallback(
        on_file_event_callback
    )
