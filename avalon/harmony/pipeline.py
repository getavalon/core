from .. import api, pipeline
from . import lib
from ..vendor import Qt

import pyblish.api


def install():
    """Install Harmony-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(harmony)`.
    """
    print("Installing Avalon Harmony...")
    pyblish.api.register_host("harmony")


def ls():
    """Yields containers from Harmony scene.

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Harmony; once loaded
    they are called 'containers'.

    Yields:
        dict: container
    """
    read_nodes = lib.send(
        {"function": "node.getNodes", "args": [["READ"]]}
    )["result"]

    for node in read_nodes:
        data = lib.read(node)

        # Skip non-tagged layers.
        if not data:
            continue

        # Filter to only containers.
        if "container" not in data["id"]:
            continue

        # Append transient data
        data["node"] = node

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
        func = """function func(args)
        {
            node.setTextAttr(args[0], "COMPOSITE_MODE", 1, "Pass Through");
        }
        func
        """
        lib.send(
            {"function": func, "args": [node]}
        )

    def process(self):
        func = """function func(args)
        {
            var nodes = node.getNodes([args[0]]);
            var node_names = [];
            for (var i = 0; i < nodes.length; ++i)
            {
              node_names.push(node.getName(nodes[i]));
            }
            return node_names
        }
        func
        """

        existing_node_names = lib.send(
            {"function": func, "args": [self.node_type]}
        )["result"]

        # Dont allow instances with the same name.
        message_box = Qt.QtWidgets.QMessageBox()
        message_box.setIcon(Qt.QtWidgets.QMessageBox.Warning)
        msg = "Instance with name \"{}\" already exists.".format(self.name)
        message_box.setText(msg)
        for name in existing_node_names:
            if self.name.lower() == name.lower():
                message_box.exec_()
                return False

        func = """function func(args)
        {
            var result_node = node.add("Top", args[0], args[1], 0, 0, 0);

            if (args.length > 2)
            {
                selected_nodes = args[2].reverse();
                for (var i = 0; i < selected_nodes.length; ++i)
                {
                    MessageLog.trace(selected_nodes[i]);
                    node.link(
                        selected_nodes[i], 0, result_node, i, false, true
                    );
                }
            }
            return result_node
        }
        func
        """

        with lib.maintained_selection() as selection:
            node = None

            if (self.options or {}).get("useSelection") and selection:
                node = lib.send(
                    {
                        "function": func,
                        "args": [self.name, self.node_type, selection]
                    }
                )["result"]
            else:
                node = lib.send(
                    {
                        "function": func,
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
                 suffix="_CON"):
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
    lib.send({"function": "node.rename", "args": [node, name + suffix]})

    data = {
        "schema": "avalon-core:container-2.0",
        "id": pipeline.AVALON_CONTAINER_ID,
        "name": name,
        "namespace": namespace,
        "loader": str(loader),
        "representation": str(context["representation"]["_id"]),
    }

    lib.imprint(node, data)

    return node
