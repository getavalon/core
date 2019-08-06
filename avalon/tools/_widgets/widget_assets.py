from . import qtawesome
from . import QtWidgets, QtCore
from . import style
from . import lib

from .._models import (
    AssetModel,
    RecursiveSortFilterProxyModel
)
from .._views import AssetsView
from .._widgets import SilosTabWidget


class AssetsWidget(QtWidgets.QWidget):
    """A Widget to display a tree of assets with filter

    To list the assets of the active project:
        >>> # widget = AssetsWidget()
        >>> # widget.refresh()
        >>> # widget.show()

    """

    silo_changed = QtCore.Signal(str)    # on silo combobox change
    assets_refreshed = QtCore.Signal()   # on model refresh
    selection_changed = QtCore.Signal()  # on view selection change
    current_changed = QtCore.Signal()    # on view current index change

    def __init__(self, silo_creatable=True, parent=None):
        super(AssetsWidget, self).__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header
        header = QtWidgets.QHBoxLayout()

        silo = SilosTabWidget(silo_creatable=silo_creatable)

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
        view = AssetsView()
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
        with lib.preserve_expanded_rows(
            self.view, column=0, role=self.model.ObjectIdRole
        ):
            with lib.preserve_selection(
                self.view, column=0, role=self.model.ObjectIdRole
            ):
                self.model.set_silo(silo)

        self.assets_refreshed.emit()

    def refresh(self):

        silos = lib._list_project_silos()
        self.silo.set_silos(silos)

        self._refresh_model()

    def get_current_silo(self):
        """Returns the currently active silo."""
        return self.silo.get_current_silo()

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
        for index in lib._iter_model_rows(self.proxy,
                                      column=0,
                                      include_root=False):
            data = index.data(self.model.NodeRole)
            name = data['name']
            if name in assets:
                selection_model.select(index, mode)

                if expand:
                    self.view.expand(index)

                # Set the currently active index
                self.view.setCurrentIndex(index)
