from .. import api
from . import lib
from ..vendor import Qt


def ls():
    """Yields containers from active Photoshop document

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Photoshop; once loaded
    they are called 'containers'

    Yields:
        dict: container

    """
    pass


class Creator(api.Creator):
    def process(self):
        # Photoshop can have multiple LayerSets with the same name, which does
        # not work with Avalon.
        msg = "Instance with name \"{}\" already exists.".format(self.name)
        for layer in lib.get_all_layers():
            if self.name.lower() == layer.Name.lower():
                msg = Qt.QtWidgets.QMessageBox()
                msg.setIcon(Qt.QtWidgets.QMessageBox.Warning)
                msg.setText(msg)
                msg.exec_()
                return False

        # Store selection because adding a group will change selection.
        selection = lib.get_selected_layers()

        # Create group/layer relationship.
        group = lib.app.ActiveDocument.LayerSets.Add()
        group.Name = self.name

        lib.imprint(group, self.data)

        # Add selection to group.
        if (self.options or {}).get("useSelection"):
            for item in selection:
                item.Move(group, lib.psPlaceAtEnd)

        return group
