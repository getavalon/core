from ....vendor import qtawesome
from ....vendor.Qt import QtWidgets, QtCore

from .... import style

from . import lib

from ..models import AssetModel, RecursiveSortFilterProxyModel
from ..views import AssetsView


class AssetsWidget(QtWidgets.QWidget):
    """A Widget to display a tree of assets with filter

    To list the assets of the active project:
        >>> # widget = AssetsWidget()
        >>> # widget.refresh()
        >>> # widget.show()

    """

    assets_refreshed = QtCore.Signal()   # on model refresh
    selection_changed = QtCore.Signal()  # on view selection change
    current_changed = QtCore.Signal()    # on view current index change

    def __init__(self, silo_creatable=None, parent=None):
        super(AssetsWidget, self).__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Tree View
        model = AssetModel(self)
        proxy = RecursiveSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        view = AssetsView()
        view.setModel(proxy)

        # Header
        header = QtWidgets.QHBoxLayout()

        icon = qtawesome.icon("fa.refresh", color=style.colors.light)
        refresh = QtWidgets.QPushButton(icon, "")
        refresh.setToolTip("Refresh items")

        filter = QtWidgets.QLineEdit()
        filter.textChanged.connect(proxy.setFilterFixedString)
        filter.setPlaceholderText("Filter assets..")

        header.addWidget(filter)
        header.addWidget(refresh)

        # Layout
        layout.addLayout(header)
        layout.addWidget(view)

        # Signals/Slots
        selection = view.selectionModel()
        selection.selectionChanged.connect(self.selection_changed)
        selection.currentChanged.connect(self.current_changed)
        refresh.clicked.connect(self.refresh)

        self.refreshButton = refresh
        self.model = model
        self.proxy = proxy
        self.view = view

    def collect_data(self):
        project = io.find_one({'type': 'project'})
        asset = io.find_one({'_id': self.get_active_asset()})

        try:
            index = self.task_view.selectedIndexes()[0]
            task = self.task_model.itemData(index)[0]
        except Exception:
            task = None
        data = {
            'project': project['name'],
            'asset': asset['name'],
            'parents': self.get_parents(asset),
            'task': task
        }
        return data

    def get_parents(self, entity):
        output = []
        if entity.get('data', {}).get('visualParent', None) is None:
            return output
        parent = io.find_one({'_id': entity['data']['visualParent']})
        output.append(parent['name'])
        output.extend(self.get_parents(parent))
        return output

    def _store_states(self):
        # Store expands
        for index in lib._iter_model_rows(
            self.proxy, column=0, include_root=False
        ):
            expanded = self.view.isExpanded(index)
            item = index.data(AssetModel.NodeRole)
            self.expand_history[str(item["_id"])] = expanded

        # store selection
        indexes = self.view.selectionModel().selectedIndexes()
        # only single selection is allowed
        for index in indexes:
            self.last_selection.append(index.data(AssetModel.NodeRole)["_id"])

    def _restore_states(self):
        if self.expand_history:
            for index in lib._iter_model_rows(
                self.proxy, column=0, include_root=False
            ):
                item = index.data(AssetModel.NodeRole)
                expanded = self.expand_history.get(str(item.get("_id", "")))
                if expanded is None:
                    continue
                self.view.setExpanded(index, expanded)

        if self.last_selection:
            self.select_assets(self.last_selection, key="_id")

    def _refresh_model(self):
        self.expand_history = {}
        self.last_selection = []

        self._store_states()
        self.model.refresh()
        self._restore_states()

        self.assets_refreshed.emit()

    def refresh(self):
        self._refresh_model()

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

    def select_assets(self, assets, expand=True, key="name"):
        """Select assets by name.

        Args:
            assets (list): List of asset names
            expand (bool): Whether to also expand to the asset in the view

        Returns:
            None

        """
        # TODO: Instead of individual selection optimize for many assets

        if not isinstance(assets, (tuple, list)):
            assets = [assets]
        assert isinstance(
            assets, (tuple, list)
        ), "Assets must be list or tuple"

        # convert to list - tuple cant be modified
        assets = list(assets)

        # Clear selection
        selection_model = self.view.selectionModel()
        selection_model.clearSelection()

        # Select
        mode = selection_model.Select | selection_model.Rows
        for index in lib._iter_model_rows(
            self.proxy, column=0, include_root=False
        ):
            # stop iteration if there are no assets to process
            if not assets:
                break

            value = index.data(self.model.NodeRole).get(key)
            if value not in assets:
                continue

            # Remove processed asset
            assets.pop(assets.index(value))

            selection_model.select(index, mode)

            if expand:
                # Expand parent index
                self.view.expand(self.proxy.parent(index))

            # Set the currently active index
            self.view.setCurrentIndex(index)
