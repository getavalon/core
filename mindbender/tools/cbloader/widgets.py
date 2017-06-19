from ...vendor.Qt import QtWidgets, QtCore, QtGui
from ... import io

from .model import SubsetsModel
from .delegates import PrettyTimeDelegate, VersionDelegate
from .lib import iter_loaders, run_loader


def _get_representations(version_id):
    """Return available representations representations for a version"""
    return [representation for representation in
            io.find({"type": "representation", "parent": version_id})
            if representation["name"] not in ("json", "source")]


class SubsetWidget(QtWidgets.QWidget):
    """A widget that lists the published subsets for an asset"""

    active_changed = QtCore.Signal()    # active index changed
    version_changed = QtCore.Signal()   # version state changed for a subset

    def __init__(self, parent=None):
        super(SubsetWidget, self).__init__(parent=parent)
        model = SubsetsModel()
        view = QtWidgets.QTreeView()
        view.setModel(model)

        view.setIndentation(5)
        view.setStyleSheet("""
            QTreeView::item{
                padding: 5px 1px;
                border: 0px;
            }
        """)
        view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        view.setSortingEnabled(True)
        view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        view.setAlternatingRowColors(True)

        # Set view delegates
        time_delegate = VersionDelegate()
        column = model.COLUMNS.index("version")
        view.setItemDelegateForColumn(column, time_delegate)

        version_delegate = PrettyTimeDelegate()
        column = model.COLUMNS.index("time")
        view.setItemDelegateForColumn(column, version_delegate)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        self.data = {
            "delegates": {
                "version": version_delegate,
                "time": time_delegate
            }
        }
        self.model = model
        self.view = view

        view.customContextMenuRequested.connect(self.on_context_menu)

    def on_context_menu(self, point):

        point_index = self.view.indexAt(point)
        if not point_index.isValid():
            return

        subset_node = point_index.data(self.model.NodeRole)
        version_document = subset_node['version_document']
        version_id = version_document['_id']

        # Get all representations for the version
        representations = _get_representations(version_id)

        # Get all representation->loader combinations available
        loaders = list()
        for representation in representations:
            for loader in iter_loaders(representation["_id"]):
                loaders.append((representation, loader))

        if not loaders:
            # no loaders available
            self.echo("No compatible loaders available for this version.")
            return

        # List the available loaders
        menu = QtWidgets.QMenu(self)
        for representation, loader in loaders:

            # Label
            label = getattr(loader, "label", None)
            if label is None:
                label = loader.__name__

            # Add the representation as suffix
            label = "{0} ({1})".format(label, representation['name'])

            action = QtWidgets.QAction(label, menu)
            action.setData((representation, loader))
            menu.addAction(action)

        # Show the context action menu
        global_point = self.view.mapToGlobal(point)
        action = menu.exec_(global_point)

        # Trigger actions
        if not action:
            return

        representation, loader = action.data()
        run_loader(loader, representation['_id'])

    def echo(self, message):
        print(message)
