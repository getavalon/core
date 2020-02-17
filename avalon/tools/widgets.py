import logging

from . import lib

from .models import AssetModel, RecursiveSortFilterProxyModel
from .views import DeselectableTreeView
from ..vendor import qtawesome, qargparse
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

    def get_active_asset_document(self):
        """Return the asset id the current asset."""
        current = self.view.currentIndex()
        return current.data(self.model.DocumentRole)

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


class OptionalMenu(QtWidgets.QMenu):
    """A subclass of `QtWidgets.QMenu` to work with `OptionalAction`

    This menu has reimplemented `mouseReleaseEvent`, `mouseMoveEvent` and
    `leaveEvent` to provide better action hightlighting and triggering for
    actions that were instances of `QtWidgets.QWidgetAction`.

    """

    def mouseReleaseEvent(self, event):
        """Emit option clicked signal if mouse released on it"""
        active = self.actionAt(event.pos())
        if active and active.use_option:
            option = active.widget.option
            if option.is_hovered(event.globalPos()):
                option.clicked.emit()
        super(OptionalMenu, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """Add highlight to active action"""
        active = self.actionAt(event.pos())
        for action in self.actions():
            action.set_highlight(action is active, event.globalPos())
        super(OptionalMenu, self).mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Remove highlight from all actions"""
        for action in self.actions():
            action.set_highlight(False)
        super(OptionalMenu, self).leaveEvent(event)


class OptionalAction(QtWidgets.QWidgetAction):
    """Menu action with option box

    A menu action like Maya's menu item with option box, implemented by
    subclassing `QtWidgets.QWidgetAction`.

    """

    def __init__(self, label, icon, use_option, parent):
        super(OptionalAction, self).__init__(parent)
        self.label = label
        self.icon = icon
        self.use_option = use_option
        self.option_tip = ""
        self.optioned = False

    def createWidget(self, parent):
        widget = OptionalActionWidget(self.label, parent)
        self.widget = widget

        if self.icon:
            widget.setIcon(self.icon)

        if self.use_option:
            widget.option.clicked.connect(self.on_option)
            widget.option.setToolTip(self.option_tip)
        else:
            widget.option.setVisible(False)

        return widget

    def set_option_tip(self, options):
        sep = "\n\n"
        mak = (lambda opt: opt["name"] + " :\n    " + opt["help"])
        self.option_tip = sep.join(mak(opt) for opt in options)

    def on_option(self):
        self.optioned = True

    def set_highlight(self, state, global_pos=None):
        body = self.widget.body
        option = self.widget.option

        role = QtGui.QPalette.Highlight if state else QtGui.QPalette.Window
        body.setBackgroundRole(role)
        body.setAutoFillBackground(state)

        if not self.use_option:
            return

        state = option.is_hovered(global_pos)
        role = QtGui.QPalette.Highlight if state else QtGui.QPalette.Window
        option.setBackgroundRole(role)
        option.setAutoFillBackground(state)


class OptionalActionWidget(QtWidgets.QWidget):
    """Main widget class for `OptionalAction`"""

    def __init__(self, label, parent=None):
        super(OptionalActionWidget, self).__init__(parent)

        body = QtWidgets.QWidget()
        body.setStyleSheet("background: transparent;")

        icon = QtWidgets.QLabel()
        label = QtWidgets.QLabel(label)
        option = OptionBox(body)

        icon.setFixedSize(24, 16)
        option.setFixedSize(30, 30)

        layout = QtWidgets.QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(icon)
        layout.addWidget(label)
        layout.addSpacing(6)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(6, 1, 2, 1)
        layout.setSpacing(0)
        layout.addWidget(body)
        layout.addWidget(option)

        body.setMouseTracking(True)
        label.setMouseTracking(True)
        option.setMouseTracking(True)
        self.setMouseTracking(True)
        self.setFixedHeight(32)

        self.icon = icon
        self.label = label
        self.option = option
        self.body = body

        # (NOTE) For removing ugly QLable shadow FX when highlighted in Nuke.
        #   See https://stackoverflow.com/q/52838690/4145300
        label.setStyle(QtWidgets.QStyleFactory.create("Plastique"))

    def setIcon(self, icon):
        pixmap = icon.pixmap(16, 16)
        self.icon.setPixmap(pixmap)


class OptionBox(QtWidgets.QLabel):
    """Option box widget class for `OptionalActionWidget`"""

    clicked = QtCore.Signal()

    def __init__(self, parent):
        super(OptionBox, self).__init__(parent)

        self.setAlignment(QtCore.Qt.AlignCenter)

        icon = qtawesome.icon("fa.sticky-note-o", color="#c6c6c6")
        pixmap = icon.pixmap(18, 18)
        self.setPixmap(pixmap)

        self.setStyleSheet("background: transparent;")

    def is_hovered(self, global_pos):
        if global_pos is None:
            return False
        pos = self.mapFromGlobal(global_pos)
        return self.rect().contains(pos)


class OptionDialog(QtWidgets.QDialog):
    """Option dialog shown by option box"""

    def __init__(self, parent=None):
        super(OptionDialog, self).__init__(parent)
        self.setModal(True)
        self._options = dict()

    def create(self, options):
        parser = qargparse.QArgumentParser(arguments=options)

        decision = QtWidgets.QWidget()
        accept = QtWidgets.QPushButton("Accept")
        cancel = QtWidgets.QPushButton("Cancel")

        layout = QtWidgets.QHBoxLayout(decision)
        layout.addWidget(accept)
        layout.addWidget(cancel)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(parser)
        layout.addWidget(decision)

        accept.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        parser.changed.connect(self.on_changed)

    def on_changed(self, argument):
        self._options[argument["name"]] = argument.read()

    def parse(self):
        return self._options.copy()
