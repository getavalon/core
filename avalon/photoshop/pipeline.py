from .. import api
from . import lib


def ls():
    """Yields containers from active Maya scene

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Maya; once loaded
    they are called 'containers'

    Yields:
        dict: container

    """
    pass


class Creator(api.Creator):
    def process(self):
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
