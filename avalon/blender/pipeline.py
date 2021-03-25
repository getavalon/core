"""Pipeline integration functions."""

import importlib
import sys
from typing import Callable, Dict, Iterator, List, Optional

import bpy

import pyblish.api
import pyblish.util

from .. import api, schema
from ..lib import find_submodule, logger
from ..pipeline import AVALON_CONTAINER_ID
from . import lib, ops

self = sys.modules[__name__]
self._events = dict()  # Registered Blender callbacks
self._parent = None  # Main window

AVALON_CONTAINERS = "AVALON_CONTAINERS"
AVALON_PROPERTY = 'avalon'
IS_HEADLESS = bpy.app.background


@bpy.app.handlers.persistent
def _on_save_pre(*args):
    api.emit("before_save", args)


@bpy.app.handlers.persistent
def _on_save_post(*args):
    api.emit("save", args)


@bpy.app.handlers.persistent
def _on_load_post(*args):
    # Detect new file or opening an existing file
    if bpy.data.filepath:
        # Likely this was an open operation since it has a filepath
        api.emit("open", args)
    else:
        api.emit("new", args)


def _register_callbacks():
    """Register callbacks for certain events."""
    def _remove_handler(handlers: List, callback: Callable):
        """Remove the callback from the given handler list."""

        try:
            handlers.remove(callback)
        except ValueError:
            pass

    # TODO (jasper): implement on_init callback?

    # Be sure to remove existig ones first.
    _remove_handler(bpy.app.handlers.save_pre, _on_save_pre)
    _remove_handler(bpy.app.handlers.save_post, _on_save_post)
    _remove_handler(bpy.app.handlers.load_post, _on_load_post)

    bpy.app.handlers.save_pre.append(_on_save_pre)
    bpy.app.handlers.save_post.append(_on_save_post)
    bpy.app.handlers.load_post.append(_on_load_post)

    logger.info("Installed event handler _on_save_pre...")
    logger.info("Installed event handler _on_save_post...")
    logger.info("Installed event handler _on_load_post...")


def _on_task_changed(*args):
    """Callback for when the task in the context is changed."""

    # TODO (jasper): Blender has no concept of projects or workspace.
    # It would be nice to override 'bpy.ops.wm.open_mainfile' so it takes the
    # workdir as starting directory.  But I don't know if that is possible.
    # Another option would be to create a custom 'File Selector' and add the
    # `directory` attribute, so it opens in that directory (does it?).
    # https://docs.blender.org/api/blender2.8/bpy.types.Operator.html#calling-a-file-selector
    # https://docs.blender.org/api/blender2.8/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
    workdir = api.Session["AVALON_WORKDIR"]
    logger.debug("New working directory: %s", workdir)


def _register_events():
    """Install callbacks for specific events."""

    api.on("taskChanged", _on_task_changed)
    logger.info("Installed event callback for 'taskChanged'...")


def install():
    """Install Blender-specific functionality for Avalon.

    This function is called automatically on calling `api.install(blender)`.
    """

    _register_callbacks()
    _register_events()

    if not IS_HEADLESS:
        ops.register()

    pyblish.api.register_host("blender")


def uninstall():
    """Uninstall Blender-specific functionality of avalon-core.

    This function is called automatically on calling `api.uninstall()`.
    """

    if not IS_HEADLESS:
        ops.unregister()

    pyblish.api.deregister_host("blender")


def reload_pipeline(*args):
    """Attempt to reload pipeline at run-time.

    Warning:
        This is primarily for development and debugging purposes and not well
        tested.

    """

    api.uninstall()

    for module in (
            "avalon.io",
            "avalon.lib",
            "avalon.pipeline",
            "avalon.blender.pipeline",
            "avalon.blender.lib",
            "avalon.tools.loader.app",
            "avalon.tools.creator.app",
            "avalon.tools.manager.app",
            "avalon.api",
            "avalon.tools",
            "avalon.blender",
    ):
        module = importlib.import_module(module)
        importlib.reload(module)

    import avalon.blender
    api.install(avalon.blender)


def _discover_gui() -> Optional[Callable]:
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

    return None


def add_to_avalon_container(container: bpy.types.Collection):
    """Add the container to the Avalon container."""

    avalon_container = bpy.data.collections.get(AVALON_CONTAINERS)
    if not avalon_container:
        avalon_container = bpy.data.collections.new(name=AVALON_CONTAINERS)

        # Link the container to the scene so it's easily visible to the artist
        # and can be managed easily. Otherwise it's only found in "Blender
        # File" view and it will be removed by Blenders garbage collection,
        # unless you set a 'fake user'.
        bpy.context.scene.collection.children.link(avalon_container)

    avalon_container.children.link(container)

    # Disable Avalon containers for the view layers.
    for view_layer in bpy.context.scene.view_layers:
        for child in view_layer.layer_collection.children:
            if child.collection == avalon_container:
                child.exclude = True


def metadata_update(node: bpy.types.bpy_struct_meta_idprop, data: Dict):
    """Imprint the node with metadata.

    Existing metadata will be updated.
    """

    if not node.get(AVALON_PROPERTY):
        node[AVALON_PROPERTY] = dict()
    for key, value in data.items():
        if value is None:
            continue
        node[AVALON_PROPERTY][key] = value


def containerise(name: str,
                 namespace: str,
                 nodes: List,
                 context: Dict,
                 loader: Optional[str] = None,
                 suffix: Optional[str] = "CON") -> bpy.types.Collection:
    """Bundle `nodes` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name: Name of resulting assembly
        namespace: Namespace under which to host container
        nodes: Long names of nodes to containerise
        context: Asset information
        loader: Name of loader used to produce this container.
        suffix: Suffix of container, defaults to `_CON`.

    Returns:
        The container assembly

    """

    node_name = f"{context['asset']['name']}_{name}"
    if namespace:
        node_name = f"{namespace}:{node_name}"
    if suffix:
        node_name = f"{node_name}_{suffix}"
    container = bpy.data.collections.new(name=node_name)
    # Link the children nodes
    for obj in nodes:
        container.objects.link(obj)

    data = {
        "schema": "avalon-core:container-2.0",
        "id": AVALON_CONTAINER_ID,
        "name": name,
        "namespace": namespace or '',
        "loader": str(loader),
        "representation": str(context["representation"]["_id"]),
    }

    metadata_update(container, data)
    add_to_avalon_container(container)

    return container


def containerise_existing(
        container: bpy.types.Collection,
        name: str,
        namespace: str,
        context: Dict,
        loader: Optional[str] = None,
        suffix: Optional[str] = "CON") -> bpy.types.Collection:
    """Imprint or update container with metadata.

    Arguments:
        name: Name of resulting assembly
        namespace: Namespace under which to host container
        context: Asset information
        loader: Name of loader used to produce this container.
        suffix: Suffix of container, defaults to `_CON`.

    Returns:
        The container assembly
    """

    node_name = container.name
    if suffix:
        node_name = f"{node_name}_{suffix}"
    container.name = node_name
    data = {
        "schema": "avalon-core:container-2.0",
        "id": AVALON_CONTAINER_ID,
        "name": name,
        "namespace": namespace or '',
        "loader": str(loader),
        "representation": str(context["representation"]["_id"]),
    }

    metadata_update(container, data)
    add_to_avalon_container(container)

    return container


def parse_container(container: bpy.types.Collection,
                    validate: bool = True) -> Dict:
    """Return the container node's full container data.

    Args:
        container: A container node name.
        validate: turn the validation for the container on or off

    Returns:
        The container schema data for this container node.

    """

    data = lib.read(container)

    # Append transient data
    data["objectName"] = container.name

    if validate:
        schema.validate(data)

    return data


def _ls():
    return lib.lsattr("id", AVALON_CONTAINER_ID)


def ls() -> Iterator:
    """List containers from active Blender scene.

    This is the host-equivalent of api.ls(), but instead of listing assets on
    disk, it lists assets already loaded in Blender; once loaded they are
    called containers.
    """

    containers = _ls()

    config = find_submodule(api.registered_config(), "blender")
    has_metadata_collector = hasattr(config, "collect_container_metadata")

    for container in containers:
        data = parse_container(container)

        # Collect custom data if property is present
        if has_metadata_collector:
            metadata = config.collect_container_metadata(container)
            data.update(metadata)

        yield data


def update_hierarchy(containers):
    """Hierarchical container support

    This is the function to support Scene Inventory to draw hierarchical
    view for containers.

    We need both parent and children to visualize the graph.

    """

    all_containers = set(_ls())  # lookup set

    for container in containers:
        # Find parent
        # FIXME (jasperge): re-evaluate this. How would it be possible
        # to 'nest' assets?  Collections can have several parents, for
        # now assume it has only 1 parent
        parent = [
            coll for coll in bpy.data.collections if container in coll.children
        ]
        for node in parent:
            if node in all_containers:
                container["parent"] = node
                break

        logger.debug("Container: %s", container)

        yield container


def publish():
    """Shorthand to publish from within host."""

    return pyblish.util.publish()


class Creator(api.Creator):
    """Base class for Creator plug-ins."""
    def process(self):
        collection = bpy.data.collections.new(name=self.data["subset"])
        bpy.context.scene.collection.children.link(collection)
        lib.imprint(collection, self.data)

        if (self.options or {}).get("useSelection"):
            for obj in lib.get_selection():
                collection.objects.link(obj)

        return collection


class Loader(api.Loader):
    """Base class for Loader plug-ins."""

    hosts = ["blender"]
