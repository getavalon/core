from .. import QtCore
from .. import DeselectableTreeView


class AssetsView(DeselectableTreeView):
    """Item view.

    This implements a context menu.

    """

    def __init__(self):
        super(AssetsView, self).__init__()
        self.setIndentation(15)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setHeaderHidden(True)
