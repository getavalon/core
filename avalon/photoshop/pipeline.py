from .. import api, pipeline
from . import lib, com_objects
from ..vendor import Qt

import pyblish.api


def install(config):
    """Install Photoshop-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(photoshop)`.
    """
    print("Installing Avalon Photoshop...")
    pyblish.api.register_host("photoshop")


def ls():
    """Yields containers from active Photoshop document

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Photoshop; once loaded
    they are called 'containers'

    Yields:
        dict: container

    """
    for layer in lib.get_layers_in_document():
        data = lib.read(layer)

        # Skip non-tagged layers.
        if not data:
            continue

        # Filter to only containers.
        if "container" not in data["id"]:
            continue

        # Append transient data
        data["layer"] = layer

        yield data


class Creator(api.Creator):
    """Creator plugin to create instances in Photoshop

    A LayerSet is created to support any number of layers in an instance. If
    the selection is used, these layers will be added to the LayerSet.
    """

    def process(self):
        # Photoshop can have multiple LayerSets with the same name, which does
        # not work with Avalon.
        msg = "Instance with name \"{}\" already exists.".format(self.name)
        for layer in lib.get_layers_in_document():
            if self.name.lower() == layer.Name.lower():
                msg = Qt.QtWidgets.QMessageBox()
                msg.setIcon(Qt.QtWidgets.QMessageBox.Warning)
                msg.setText(msg)
                msg.exec_()
                return False

        # Store selection because adding a group will change selection.
        with lib.maintained_selection() as selection:
            # Create group/layer relationship.
            group = lib.app().ActiveDocument.LayerSets.Add()
            group.Name = self.name

            lib.imprint(group, self.data)

            # Add selection to group.
            if (self.options or {}).get("useSelection"):
                for item in selection:
                    item.Move(group, com_objects.constants().psPlaceAtEnd)

        return group


def containerise(name,
                 namespace,
                 layer,
                 context,
                 loader=None,
                 suffix="_CON"):
    """Imprint layer with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        layer (COMObject): Layer to containerise
        context (dict): Asset information
        loader (str, optional): Name of loader used to produce this container.
        suffix (str, optional): Suffix of container, defaults to `_CON`.

    Returns:
        container (str): Name of container assembly
    """
    layer.Name = name + suffix

    data = {
        "schema": "avalon-core:container-2.0",
        "id": pipeline.AVALON_CONTAINER_ID,
        "name": name,
        "namespace": namespace,
        "loader": str(loader),
        "representation": str(context["representation"]["_id"]),
    }

    lib.imprint(layer, data)

    return layer
