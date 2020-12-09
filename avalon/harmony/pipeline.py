from pathlib import Path

from .. import api, pipeline
from . import lib

import pyblish.api


def inject_avalon_js():
    """Inject AvalonHarmony.js into Harmony."""
    avalon_harmony_js = Path(__file__).parent.joinpath("js/AvalonHarmony.js")
    script = avalon_harmony_js.read_text()
    # send AvalonHarmony.js to Harmony
    lib.send({"script": script})


def install():
    """Install Harmony-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(harmony)`.
    """
    print("Installing Avalon Harmony...")
    pyblish.api.register_host("harmony")
    api.on("application.launched", inject_avalon_js)


def ls():
    """Yields containers from Harmony scene.

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Harmony; once loaded
    they are called 'containers'.

    Yields:
        dict: container
    """
    objects = lib.get_scene_data() or {}
    for _, data in objects.items():
        # Skip non-tagged objects.
        if not data:
            continue

        # Filter to only containers.
        if "container" not in data.get("id"):
            continue

        yield data


class Creator(api.Creator):
    """Creator plugin to create instances in Harmony.

    By default a Composite node is created to support any number of nodes in
    an instance, but any node type is supported.
    If the selection is used, the selected nodes will be connected to the
    created node.
    """

    node_type = "COMPOSITE"

    def setup_node(self, node):
        """Prepare node as container.

        Args:
            node (str): Path to node.
        """
        lib.send(
            {
                "function": "AvalonHarmony.setupNodeForCreator",
                "args": node
            }
        )

    def process(self):
        """Plugin entry point."""
        existing_node_names = lib.send(
            {
                "function": "AvalonHarmony.getNodesNamesByType",
                "args": self.node_type
            })["result"]

        # Dont allow instances with the same name.
        msg = "Instance with name \"{}\" already exists.".format(self.name)
        for name in existing_node_names:
            if self.name.lower() == name.lower():
                lib.send(
                    {
                        "function": "AvalonHarmony.message", "args": msg
                    }
                )
                return False

        with lib.maintained_selection() as selection:
            node = None

            if (self.options or {}).get("useSelection") and selection:
                node = lib.send(
                    {
                        "function": "AvalonHarmony.createContainer",
                        "args": [self.name, self.node_type, selection[-1]]
                    }
                )["result"]
            else:
                node = lib.send(
                    {
                        "function": "AvalonHarmony.createContainer",
                        "args": [self.name, self.node_type]
                    }
                )["result"]

            lib.imprint(node, self.data)
            self.setup_node(node)

        return node


def containerise(name,
                 namespace,
                 node,
                 context,
                 loader=None,
                 suffix=None,
                 nodes=[]):
    """Imprint node with metadata.

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly.
        namespace (str): Namespace under which to host container.
        node (str): Node to containerise.
        context (dict): Asset information.
        loader (str, optional): Name of loader used to produce this container.
        suffix (str, optional): Suffix of container, defaults to `_CON`.

    Returns:
        container (str): Path of container assembly.
    """
    data = {
        "schema": "avalon-core:container-2.0",
        "id": pipeline.AVALON_CONTAINER_ID,
        "name": name,
        "namespace": namespace,
        "loader": str(loader),
        "representation": str(context["representation"]["_id"]),
        "nodes": nodes
    }

    lib.imprint(node, data)

    return node
