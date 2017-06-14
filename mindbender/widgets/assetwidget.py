import contextlib

from . import style
from .. import io
from .tree import TreeModel, Node
from .proxy import RecursiveSortFilterProxyModel
from .deselectabletreeview import DeselectableTreeView
from ..vendor import qtawesome as qta
from ..vendor.Qt import QtWidgets, QtCore, QtGui

import logging
log = logging.getLogger(__name__)


def _iter_model_rows(model,
                     column,
                     include_root=False):
    """Iterate over all row indices in a model."""
    indices = [QtCore.QModelIndex()]  # start iteration at root

    for index in indices:

        # Add children to the iterations
        child_rows = model.rowCount(index)
        for child_row in range(child_rows):
            child_index = model.index(child_row, column, index)
            indices.append(child_index)

        if not include_root and not index.isValid():
            continue

        yield index


@contextlib.contextmanager
def preserve_expanded_rows(tree_view,
                           column=0,
                           role=QtCore.Qt.DisplayRole):
    """Preserves expanded row in QTreeView by column's data role.

    This function is created to maintain the expand vs collapse status of
    the model items. When refresh is triggered the items which are expanded
    will stay expanded and vise versa.

    :param tree_view: the tree view which is nested in the application
    :type tree_view: QWidgets.QTreeView

    :param column: the column to retrieve the data from
    :type column: int

    :param role: the role which dictates what will be returned
    :type role: int

    :return: None
    """
    model = tree_view.model()

    expanded = set()

    for index in _iter_model_rows(model,
                                  column=column,
                                  include_root=False):
        if tree_view.isExpanded(index):
            value = index.data(role)
            expanded.add(value)

    try:
        yield
    finally:
        if not expanded:
            return

        for index in _iter_model_rows(model,
                                      column=column,
                                      include_root=False):
            value = index.data(role)
            state = value in expanded
            if state:
                tree_view.expand(index)
            else:
                tree_view.collapse(index)


@contextlib.contextmanager
def preserve_selection(tree_view,
                       column=0,
                       role=QtCore.Qt.DisplayRole,
                       current_index=True):
    """Preserves row selection in QTreeView by column's data role.

    This function is created to maintain the selection status of
    the model items. When refresh is triggered the items which are expanded
    will stay expanded and vise versa.

    :param tree_view: the tree view which is nested in the application
    :type tree_view: QWidgets.QTreeView

    :param column: the column to retrieve the data from
    :type column: int

    :param role: the role which dictates what will be returned
    :type role: int

    :return: None
    """

    model = tree_view.model()
    selection_model = tree_view.selectionModel()
    flags = selection_model.Select | selection_model.Rows

    if current_index:
        current_index_value = tree_view.currentIndex().data(role)
    else:
        current_index_value = None

    selected_rows = selection_model.selectedRows()
    if not selected_rows:
        yield
        return

    selected = set(row.data(role) for row in selected_rows)
    try:
        yield
    finally:
        if not selected:
            return

        # Go through all indices, select the ones with similar data
        for index in _iter_model_rows(model,
                                      column=column,
                                      include_root=False):

            value = index.data(role)
            state = value in selected
            if state:
                selection_model.select(index, flags)

            if current_index_value and value == current_index_value:
                tree_view.setCurrentIndex(index)


def _list_project_silos():
    """List the silos from the project's configuration"""
    silos = io.distinct("silo")

    if not silos:
        project = io.find_one({"type": "project"})
        log.warning("Project '%s' has no active silos", project['name'])

    return list(sorted(silos))


class AssetModel(TreeModel):
    """A model listing assets in the silo in the activec project.
    
    The assets are displayed in a treeview, they are visually parented by
    a `visualParent` field in the database containing an `_id` to a parent
    asset.
    
    """

    COLUMNS = ["label", "tags", "deprecated"]
    Name = 0
    Deprecated = 2
    ObjectId = 3

    ObjectIdRole = QtCore.Qt.UserRole + 1

    def __init__(self, silo=None, parent=None):
        super(AssetModel, self).__init__(parent=parent)

        self._silo = None

        if silo is not None:
            self.set_silo(silo, refresh=True)

    def set_silo(self, silo, refresh=True):
        """Set the root path to the ItemType root."""
        self._silo = silo
        if refresh:
            self.refresh()

    def _add_hierarchy(self, parent=None):

        # Find the assets under the parent
        find_data = {
            "type": "asset",
            "silo": self._silo,
        }
        if parent is None:
            # if not a parent find all that are parented to the project
            # or do *not* have a visualParent field at all
            find_data['$or'] = [
                {'visualParent': {'$exists': False}},
                {'visualParent': None}
            ]
        else:
            find_data["visualParent"] = parent['_id']

        assets = io.find(find_data)

        for asset in assets:

            # get label from data, otherwise use name
            label = asset.get("data", {}).get("label", asset['name'])

            # store for the asset for optimization
            deprecated = "deprecated" in asset.get("tags", [])

            node = Node({
                "_id": asset['_id'],
                "name": asset["name"],
                "label": label,
                "type": asset['type'],
                "tags": ", ".join(asset.get("tags", [])),
                "deprecated": deprecated,
            })
            self.add_child(node, parent=parent)

            # Add asset's children recursively
            self._add_hierarchy(node)

    def refresh(self):
        """Refresh the data for the model."""

        self.clear()
        self.beginResetModel()
        if self._silo:
            self._add_hierarchy(parent=None)
        self.endResetModel()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):

        if role == QtCore.Qt.DecorationRole:        # icon

            column = index.column()
            node = index.internalPointer()
            if column == self.Name:

                # define color, including darker state
                # when the asset is deprecated
                color = style.default
                if node.get("deprecated", False):
                    color = QtGui.QColor(color).darker(250)

                # If it has children show a full folder
                if self.rowCount(index) > 0:
                    return qta.icon("fa.folder", color=color)
                else:
                    return qta.icon("fa.folder-o", color=color)

        if role == QtCore.Qt.ForegroundRole:        # font color

            node = index.internalPointer()
            if "deprecated" in node.get("tags", []):
                return QtGui.QColor(style.light).darker(250)

        if role == self.ObjectIdRole:
            node = index.internalPointer()
            return node.get("_id", None)

        return super(AssetModel, self).data(index, role)


class AssetView(DeselectableTreeView):
    """Item view.

    This implements a context menu.

    """
    def __init__(self):
        super(AssetView, self).__init__()
        self.setIndentation(15)
        #self.setHeaderHidden(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    #     self.customContextMenuRequested.connect(self.on_contextMenu)
    #
    # def on_contextMenu(self, point):
    #     """Context menu for the item hierarchy view"""
    #
    #     index = self.currentIndex()
    #     if not index or not index.isValid():
    #         return
    #
    #     path = get_data(index, AssetModel.FilePathRole)
    #     if not path or not os.path.exists(path):
    #         logger.error("Item path does not exist. This is a bug.")
    #         return
    #
    #     menu = QtWidgets.QMenu(self)
    #
    #     metadata = {"path": path}
    #     from cbra.actions.generic import ShowPathInExplorerAction
    #     from cbra.action import _to_action
    #
    #     action = _to_action(ShowPathInExplorerAction(),
    #                         metadata,
    #                         parent=menu)
    #
    #     menu.addAction(action)
    #
    #     # Start context menu
    #     globalPoint = self.mapToGlobal(point)
    #     menu.exec_(globalPoint)


class SiloTabWidget(QtWidgets.QTabWidget):
    """Silo widget
    
    Allows to add a silo, with "+" tab.
    
    Note:
        When no silos are present an empty stub silo is added to
        use as the "blank" tab to start on, so the + tab becomes
        clickable.
    
    """
    silo_changed = QtCore.Signal(str)
    silo_added = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(SiloTabWidget, self).__init__(parent=parent)
        self._previous_tab_index = -1
        self.set_silos([])

        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedHeight(28)
        font = QtGui.QFont()
        font.setBold(True)
        self.setFont(font)

        #self.setSizePolicy(QtGui)

        self.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):

        if index == self._previous_tab_index:
            return

        # If it's the last tab
        num = self.count()
        if index == num - 1:
            self.on_add_silo()
            self.setCurrentIndex(self._previous_tab_index)
            return

        silo = self.tabText(index)
        self.silo_changed.emit(silo)

        # Store for the next calls
        self._previous_tab_index = index

    def set_silos(self, silos):

        current_silo = self.get_current_silo()

        if not silos:
            # Add an emtpy stub tab to start on.
            silos = [""]

        # Populate the silos without emitting signals
        self.blockSignals(True)
        self.clear()
        for silo in sorted(silos):
            self.addTab(QtWidgets.QWidget(), silo)

        # Add the "+" tab
        self.addTab(QtWidgets.QWidget(), "+")

        self.set_current_silo(current_silo)
        self.blockSignals(False)

        # Assume the current index is "fine"
        self._previous_tab_index = self.currentIndex()

        # Only emit a silo changed signal if the new signal
        # after refresh is not the same as prior to it (e.g.
        # when the silo was removed, or alike.)
        if current_silo != self.get_current_silo():
            self.currentChanged.emit(self.currentIndex())

    def set_current_silo(self, silo):
        """Set the active silo by name or index.

        Args:
            silo (str or int): The silo name or index.
            emit (bool): Whether to emit the change signals

        """

        # Already set
        if silo == self.get_current_silo():
            return

        # Otherwise change the silo box to the name
        for i in range(self.count()):
            text = self.tabText(i)
            if text == silo:
                self.setCurrentIndex(i)
                break

    def get_current_silo(self):
        index = self.currentIndex()
        return self.tabText(index)

    def on_add_silo(self):
        silo, state = QtWidgets.QInputDialog.getText(self,
                                                     "Silo name",
                                                     "Create new silo:")
        if not state or not silo:
            return

        self.add_silo(silo)

    def get_silos(self):
        """Return the currently available silos"""

        # Ignore first tab if empty
        # Ignore the last tab because it is the "+" tab
        silos = []
        for i in range(self.count() - 1):
            label = self.tabText(i)
            if i == 0 and not label:
                continue
            silos.append(label)
        return silos

    def add_silo(self, silo):

        # Add the silo
        silos = self.get_silos()
        silos.append(silo)
        silos = list(set(silos))  # ensure unique
        self.set_silos(silos)
        self.set_current_silo(silo)

        self.silo_added.emit(silo)
        self.silo_changed.emit(silo)


class AssetWidget(QtWidgets.QWidget):
    """A Widget to display a tree of assets with filter

    To list the assets of the active project:
        >>> # widget = AssetWidget()
        >>> # widget.refresh()
        >>> # widget.show()

    """

    silo_changed = QtCore.Signal(str)    # on silo combobox change
    assets_refreshed = QtCore.Signal()   # on model refresh
    selection_changed = QtCore.Signal()  # on view selection change
    current_changed = QtCore.Signal()    # on view current index change

    def __init__(self, parent=None):
        super(AssetWidget, self).__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QtWidgets.QHBoxLayout()

        silo = SiloTabWidget()

        icon = qta.icon("fa.refresh", color=style.light)
        refresh = QtWidgets.QPushButton(icon, "")
        refresh.setToolTip("Refresh items")

        header.addWidget(silo)
        header.addStretch(1)
        header.addWidget(refresh)

        # Tree View
        model = AssetModel()
        proxy = RecursiveSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        view = AssetView()
        view.setModel(proxy)

        filter = QtWidgets.QLineEdit()
        filter.textChanged.connect(proxy.setFilterFixedString)
        filter.setPlaceholderText("Filter")

        # Layout
        layout.addLayout(header)
        layout.addWidget(view)
        layout.addWidget(filter)

        # Signals/Slots
        selection = view.selectionModel()
        selection.selectionChanged.connect(self.selection_changed)
        selection.currentChanged.connect(self.current_changed)
        silo.silo_changed.connect(self._on_silo_changed)
        refresh.clicked.connect(self.refresh)

        self.refreshButton = refresh
        self.silo = silo
        self.model = model
        self.proxy = proxy
        self.view = view

    def _on_silo_changed(self, index):
        """Callback for silo change"""

        self._refresh_model()
        silo = self.get_current_silo()
        self.silo_changed.emit(silo)
        self.selection_changed.emit()

    def _refresh_model(self):

        silo = self.get_current_silo()
        with preserve_expanded_rows(self.view,
                                    column=0,
                                    role=self.model.ObjectIdRole):
            with preserve_selection(self.view,
                                    column=0,
                                    role=self.model.ObjectIdRole):
                self.model.set_silo(silo)

        self.assets_refreshed.emit()

    def refresh(self):

        silos =_list_project_silos()
        self.silo.set_silos(silos)

        self._refresh_model()

    def get_current_silo(self):
        """Returns the currently active silo."""
        return self.silo.get_current_silo()

    def get_active_asset(self):
        """Return the asset id the current asset."""
        current = self.view.currentIndex()
        return current.data(self.model.ObjectIdRole)

    def get_selected_assets(self):
        """Return the assets' ids that are selected."""
        selection = self.view.selectionModel()
        rows = selection.selectedRows()
        return [row.data(self.model.ObjectIdRole) for row in rows]

    # def set_asset_selection(self, assets, expand=False):
    #     """Select the relative items.
    #
    #     Also expands the tree view when `expand=True`.
    #
    #     Args:
    #         assets (list): A list of asset names.
    #
    #     """
    #
    #     # TODO: Implement to select by unique asset "name"
    #     if not isinstance(assets, (list, tuple)):
    #         raise TypeError("Set items takes a list of items to set")
    #
    #     selection_model = self.view.selectionModel()
    #     selection_model.clearSelection()
    #     mode = selection_model.Select | selection_model.Rows
    #
    #     for asset in assets:
    #
    #         index = self.model.find_index(asset)
    #         if not index or not index.isValid():
    #             continue
    #
    #         index = self.proxy.mapFromSource(index)
    #         selection_model.select(index, mode)
    #
    #         if expand:
    #             # TODO: Implement expanding to the item
    #             pass
    #
    #     self.selection_changed.emit()
