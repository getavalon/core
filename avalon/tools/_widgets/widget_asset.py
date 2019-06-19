import contextlib
from . import QtCore, QtWidgets
from . import qtawesome, style, io
# from .lib import (
#     _iter_model_rows,
#     _list_project_silos,
#     preserve_selection,
#     preserve_expanded_rows
# )
from . import SiloTabWidget
from .._models import AssetModel, RecursiveSortFilterProxyModel
from .._views import AssetView


def _iter_model_rows(model, column, include_root=False):
    """Iterate over all row indices in a model"""
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
def preserve_expanded_rows(tree_view, column=0, role=QtCore.Qt.DisplayRole):
    """Preserves expanded row in QTreeView by column's data role.

    This function is created to maintain the expand vs collapse status of
    the model items. When refresh is triggered the items which are expanded
    will stay expanded and vise versa.

    Arguments:
        tree_view (QWidgets.QTreeView): the tree view which is
            nested in the application
        column (int): the column to retrieve the data from
        role (int): the role which dictates what will be returned

    Returns:
        None

    """

    model = tree_view.model()

    expanded = set()

    for index in _iter_model_rows(model, column=column, include_root=False):
        if tree_view.isExpanded(index):
            value = index.data(role)
            expanded.add(value)

    try:
        yield
    finally:
        if not expanded:
            return

        for index in _iter_model_rows(
            model, column=column, include_root=False
        ):
            value = index.data(role)
            state = value in expanded
            if state:
                tree_view.expand(index)
            else:
                tree_view.collapse(index)


@contextlib.contextmanager
def preserve_selection(
    tree_view, column=0, role=QtCore.Qt.DisplayRole, current_index=True
):
    """Preserves row selection in QTreeView by column's data role.

    This function is created to maintain the selection status of
    the model items. When refresh is triggered the items which are expanded
    will stay expanded and vise versa.

        tree_view (QWidgets.QTreeView): the tree view nested in the application
        column (int): the column to retrieve the data from
        role (int): the role which dictates what will be returned

    Returns:
        None

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
        for index in _iter_model_rows(
            model, column=column, include_root=False
        ):
            value = index.data(role)
            state = value in selected
            if state:
                tree_view.scrollTo(index)  # Ensure item is visible
                selection_model.select(index, flags)

            if current_index_value and value == current_index_value:
                tree_view.setCurrentIndex(index)


def _list_project_silos():
    """List the silos from the project's configuration"""
    # old way: silos = io.distinct("silo")
    # new, Backwards compatible way to get all silos from DB:
    silos = [s['name'] for s in io.find({"type": "asset", "silo": None})]
    silos_old = io.distinct("silo")
    for silo in silos_old:
        if silo not in silos and silo is not None:
            silos.append(silo)

    if not silos:
        project = io.find_one({"type": "project"})
        log.warning("Project '%s' has no active silos", project['name'])

    return list(sorted(silos))


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
        layout.setSpacing(4)

        # Header
        header = QtWidgets.QHBoxLayout()

        silo = SiloTabWidget()

        icon = qtawesome.icon("fa.refresh", color=style.colors.light)
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
        filter.setPlaceholderText("Filter assets..")

        # Layout
        layout.addLayout(header)
        layout.addWidget(filter)
        layout.addWidget(view)

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

    def _on_silo_changed(self):
        """Callback for silo change"""

        self._refresh_model()
        silo = self.get_current_silo()
        self.silo_changed.emit(silo)
        self.selection_changed.emit()

    def _refresh_model(self):

        silo = self.get_current_silo()
        with preserve_expanded_rows(
            self.view, column=0, role=self.model.ObjectIdRole
        ):
            with preserve_selection(
                self.view, column=0, role=self.model.ObjectIdRole
            ):
                self.model.set_silo(silo)

        self.assets_refreshed.emit()

    def refresh(self):

        silos = _list_project_silos()
        self.silo.set_silos(silos)
        # set first silo as active so tasks are shown
        if len(silos) > 0:
            self.silo.set_current_silo(self.silo.tabText(0))
        self._refresh_model()

    def get_current_silo(self):
        """Returns the currently active silo."""
        return self.silo.get_current_silo()

    def get_silo_object(self, silo_name=None):
        """ Returns silo object from db. None if not found.
        Current silo is found if silo_name not entered."""
        if silo_name is None:
            silo_name = self.get_current_silo()
        try:
            return io.find_one({"type": "asset", "name": silo_name})
        except Exception:
            return None

    def get_active_asset(self):
        """Return the asset id the current asset."""
        current = self.view.currentIndex()
        return current.data(self.model.ObjectIdRole)

    def get_active_index(self):
        return self.view.currentIndex()

    def get_selected_assets(self):
        """Return the assets' ids that are selected."""
        selection = self.view.selectionModel()
        rows = selection.selectedRows()
        return [row.data(self.model.ObjectIdRole) for row in rows]

    def set_silo(self, silo):
        """Set the active silo tab"""
        self.silo.set_current_silo(silo)

    def select_assets(self, assets, expand=True):
        """Select assets by name.

        Args:
            assets (list): List of asset names
            expand (bool): Whether to also expand to the asset in the view

        Returns:
            None

        """
        # TODO: Instead of individual selection optimize for many assets

        assert isinstance(assets,
                          (tuple, list)), "Assets must be list or tuple"

        # Clear selection
        selection_model = self.view.selectionModel()
        selection_model.clearSelection()

        # Select
        mode = selection_model.Select | selection_model.Rows
        for index in _iter_model_rows(
            self.proxy, column=0, include_root=False
        ):
            data = index.data(self.model.NodeRole)
            name = data['name']
            if name in assets:
                selection_model.select(index, mode)

                if expand:
                    self.view.expand(index)

                # Set the currently active index
                self.view.setCurrentIndex(index)
