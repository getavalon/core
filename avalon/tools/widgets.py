import logging

from . import lib

from .models import AssetModel, RecursiveSortFilterProxyModel
from .views import AssetsView
from .delegates import AssetDelegate
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

    assets_refreshed = QtCore.Signal()   # on model refresh
    selection_changed = QtCore.Signal()  # on view selection change
    current_changed = QtCore.Signal()    # on view current index change

    def __init__(self, multiselection=False, parent=None):
        super(AssetWidget, self).__init__(parent=parent)
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
        view.setProperty("multiselection", multiselection)
        if multiselection:
            asset_delegate = AssetDelegate()
            view.setSelectionMode(view.ExtendedSelection)
            view.setItemDelegate(asset_delegate)

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

    def _refresh_model(self):
        with lib.preserve_states(
            self.view, column=0, role=self.model.ObjectIdRole
        ):
            self.model.refresh()

        self.assets_refreshed.emit()

    def refresh(self):
        self._refresh_model()

    def get_active_asset(self):
        """Return the asset item of the current selection."""
        current = self.view.currentIndex()
        return current.data(self.model.ItemRole)

    def get_active_asset_document(self):
        """Return the asset document of the current selection."""
        current = self.view.currentIndex()
        return current.data(self.model.DocumentRole)

    def get_active_index(self):
        return self.view.currentIndex()

    def get_selected_assets(self):
        """Return the documents of selected assets."""
        selection = self.view.selectionModel()
        rows = selection.selectedRows()
        assets = [row.data(self.model.DocumentRole) for row in rows]

        # NOTE: skip None object assumed they are silo (backwards comp.)
        return [asset for asset in assets if asset]

    def select_assets(self, assets, expand=True, key="name"):
        """Select assets by item key.

        Args:
            assets (list): List of asset values that can be found under
                specified `key`
            expand (bool): Whether to also expand to the asset in the view
            key (string): Key that specifies where to look for `assets` values

        Returns:
            None

        Default `key` is "name" in that case `assets` should contain single
        asset name or list of asset names. (It is good idea to use "_id" key
        instead of name in that case `assets` must contain `ObjectId` object/s)
        It is expected that each value in `assets` will be found only once.
        If the filters according to the `key` and `assets` correspond to
        the more asset, only the first found will be selected.

        """

        if not isinstance(assets, (tuple, list)):
            assets = [assets]

        # convert to list - tuple cant be modified
        assets = set(assets)

        # Clear selection
        selection_model = self.view.selectionModel()
        selection_model.clearSelection()

        # Select
        mode = selection_model.Select | selection_model.Rows
        for index in lib.iter_model_rows(
            self.proxy, column=0, include_root=False
        ):
            # stop iteration if there are no assets to process
            if not assets:
                break

            value = index.data(self.model.ItemRole).get(key)
            if value not in assets:
                continue

            # Remove processed asset
            assets.discard(value)

            selection_model.select(index, mode)
            if expand:
                # Expand parent index
                self.view.expand(self.proxy.parent(index))

            # Set the currently active index
            self.view.setCurrentIndex(index)


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
