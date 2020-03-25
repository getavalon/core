from .. import api
from . import lib
from ..vendor import Qt

import pyblish.api


def install():
    """Install Photoshop-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(photoshop)`.
    """
    print("Installing Avalon Harmony...")
    pyblish.api.register_host("harmony")


def ls():
    pass


class Creator(api.Creator):
    """Creator plugin to create instances in Harmony.
    A Composite node is created to support any number of nodes in an instance.
    If the selection is used, these nodes will be connected to the composite
    node.
    """

    def process(self):
        func = """function get_composites()
        {
            var nodes = node.getNodes(["COMPOSITE"]);
            var node_names = [];
            for (var i = 0; i < nodes.length; ++i)
            {
              node_names.push(node.getName(nodes[i]));
            }
            return node_names
        }
        get_composites
        """

        composite_names = lib.server.send({"function": func})["result"]

        # Dont allow instances with the same name.
        message_box = Qt.QtWidgets.QMessageBox()
        message_box.setIcon(Qt.QtWidgets.QMessageBox.Warning)
        msg = "Instance with name \"{}\" already exists.".format(self.name)
        message_box.setText(msg)
        for name in composite_names:
            if self.name.lower() == name.lower():
                message_box.exec_()
                return False

        # Have to use "args" else the selected_nodes list/array is not
        # preserved.
        create_composite = """function create_composite(args)
        {
            var comp = node.add("Top", args[0], "COMPOSITE", 0, 0, 0);
            node.setTextAttr(comp, "COMPOSITE_MODE", 1, "Pass Through");

            if (args.length > 1)
            {
                selected_nodes = args[1].reverse();
                for (var i = 0; i < selected_nodes.length; ++i)
                {
                    MessageLog.trace(selected_nodes[i]);
                    node.link(selected_nodes[i], 0, comp, i, false, true);
                }
            }
            return comp
        }
        create_composite
        """

        with lib.maintained_selection() as selection:
            composite = None

            if (self.options or {}).get("useSelection") and selection:
                composite = lib.server.send(
                    {
                        "function": create_composite,
                        "args": [self.name, selection]
                    }
                )["result"]
            else:
                composite = lib.server.send(
                    {
                        "function": create_composite,
                        "args": [self.name]
                    }
                )["result"]

            lib.imprint(composite, self.data)

        return composite
