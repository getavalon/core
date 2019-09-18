import logging

from . import lib

from .models import AssetModel, RecursiveSortFilterProxyModel
from .views import DeselectableTreeView
from ..vendor import qtawesome
from ..vendor.Qt import QtWidgets, QtCore, QtGui

from .. import style
from .. import io

log = logging.getLogger(__name__)


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

    def __init__(self, silo_creatable=True, parent=None):
        super(AssetWidget, self).__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header
        header = QtWidgets.QHBoxLayout()

        silo = SiloTabWidget(silo_creatable=silo_creatable)

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

        view = DeselectableTreeView()
        view.setIndentation(15)
        view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        view.setHeaderHidden(True)
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
        with lib.preserve_expanded_rows(self.view,
                                        column=0,
                                        role=self.model.ObjectIdRole):
            with lib.preserve_selection(self.view,
                                        column=0,
                                        role=self.model.ObjectIdRole):
                self.model.set_silo(silo)

        self.assets_refreshed.emit()

    def refresh(self):

        silos = _list_project_silos()
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
        for index in lib.iter_model_rows(self.proxy,
                                         column=0,
                                         include_root=False):
            data = index.data(self.model.ItemRole)
            name = data["name"]
            if name in assets:
                selection_model.select(index, mode)

                if expand:
                    self.view.expand(index)

                # Set the currently active index
                self.view.setCurrentIndex(index)


class SiloTabWidget(QtWidgets.QTabBar):
    """Silo widget

    Allows to add a silo, with "+" tab.

    Note:
        When no silos are present an empty stub silo is added to
        use as the "blank" tab to start on, so the + tab becomes
        clickable.

    """

    silo_changed = QtCore.Signal(str)
    silo_added = QtCore.Signal(str)

    def __init__(self, silo_creatable=True, parent=None):
        super(SiloTabWidget, self).__init__(parent=parent)
        self.silo_creatable = silo_creatable
        self._previous_tab_index = -1
        self.set_silos([])

        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedHeight(28)
        font = QtGui.QFont()
        font.setBold(True)
        self.setFont(font)

        self.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):

        if index == self._previous_tab_index:
            return

        # If it's the last tab
        num = self.count()
        if self.silo_creatable and index == num - 1:
            self.on_add_silo()
            self.setCurrentIndex(self._previous_tab_index)
            return

        silo = self.tabText(index)
        self.silo_changed.emit(silo)

        # Store for the next calls
        self._previous_tab_index = index

    def clear(self):
        """Removes all tabs.

        Implemented similar to `QTabWidget.clear()`

        """
        for i in range(self.count()):
            self.removeTab(0)

    def set_silos(self, silos):

        current_silo = self.get_current_silo()

        if not silos:
            # Add an emtpy stub tab to start on.
            silos = [""]

        # Populate the silos without emitting signals
        self.blockSignals(True)
        self.clear()
        for silo in sorted(silos):
            self.addTab(silo)

        if self.silo_creatable:
            # Add the "+" tab
            self.addTab("+")

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
        self.silo_added.emit(silo)

        self.set_current_silo(silo)


def _list_project_silos():
    """List the silos from the project's configuration"""
    silos = io.distinct("silo")

    if not silos:
        project = io.find_one({"type": "project"})
        log.warning("Project '%s' has no active silos", project["name"])

    return list(sorted(silos))
