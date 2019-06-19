from . import QtCore, QtWidgets
from . import io, lib


class FamilyListWidget(QtWidgets.QListWidget):
    """A Widget that lists all available families"""

    NameRole = QtCore.Qt.UserRole + 1
    active_changed = QtCore.Signal(list)

    def __init__(self, family_config, parent=None):
        super(FamilyListWidget, self).__init__(parent=parent)
        self.family_config = family_config
        multi_select = QtWidgets.QAbstractItemView.ExtendedSelection
        self.setSelectionMode(multi_select)
        self.setAlternatingRowColors(True)
        # Enable RMB menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_right_mouse_menu)

        self.itemChanged.connect(self._on_item_changed)

    def refresh(self):
        """Refresh the listed families.

        This gets all unique families and adds them as checkable items to
        the list.

        """

        family = io.distinct("data.family")
        families = io.distinct("data.families")
        unique_families = list(set(family + families))

        # Rebuild list
        self.blockSignals(True)
        self.clear()
        for name in sorted(unique_families):

            family = lib.get(self.family_config, name)
            label = family.get("label", name)
            icon = family.get("icon", None)

            # TODO: This should be more managable by the artist
            # Temporarily implement support for a default state in the project
            # configuration
            state = family.get("state", True)
            state = QtCore.Qt.Checked if state else QtCore.Qt.Unchecked

            item = QtWidgets.QListWidgetItem(parent=self)
            item.setText(label)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setData(self.NameRole, name)
            item.setCheckState(state)

            if icon:
                item.setIcon(icon)

            self.addItem(item)
        self.blockSignals(False)

        self.active_changed.emit(self.get_filters())

    def get_filters(self):
        """Return the checked family items"""

        items = [self.item(i) for i in
                 range(self.count())]

        return [item.data(self.NameRole) for item in items if
                item.checkState() == QtCore.Qt.Checked]

    def _on_item_changed(self):
        self.active_changed.emit(self.get_filters())

    def _set_checkstate_all(self, state):
        _state = QtCore.Qt.Checked if state is True else QtCore.Qt.Unchecked
        self.blockSignals(True)
        for i in range(self.count()):
            item = self.item(i)
            item.setCheckState(_state)
        self.blockSignals(False)
        self.active_changed.emit(self.get_filters())

    def show_right_mouse_menu(self, pos):
        """Build RMB menu under mouse at current position (within widget)"""

        # Get mouse position
        globalpos = self.viewport().mapToGlobal(pos)

        menu = QtWidgets.QMenu(self)

        # Add enable all action
        state_checked = QtWidgets.QAction(menu, text="Enable All")
        state_checked.triggered.connect(
            lambda: self._set_checkstate_all(True))
        # Add disable all action
        state_unchecked = QtWidgets.QAction(menu, text="Disable All")
        state_unchecked.triggered.connect(
            lambda: self._set_checkstate_all(False))

        menu.addAction(state_checked)
        menu.addAction(state_unchecked)

        menu.exec_(globalpos)
