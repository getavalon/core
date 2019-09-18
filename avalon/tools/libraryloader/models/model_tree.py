from .model_item import Item
from ....vendor.Qt import QtCore


class TreeModel(QtCore.QAbstractItemModel):

    COLUMNS = list()
    ItemRole = QtCore.Qt.UserRole + 1

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self._root_item = Item()

    def rowCount(self, parent):
        if parent.isValid():
            item = parent.internalPointer()
        else:
            item = self._root_item

        return item.childCount()

    def columnCount(self, parent):
        return len(self.COLUMNS)

    def data(self, index, role):

        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:

            item = index.internalPointer()
            column = index.column()

            key = self.COLUMNS[column]
            return item.get(key, None)

        if role == self.ItemRole:
            return index.internalPointer()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """Change the data on the items.

        Returns:
            bool: Whether the edit was successful
        """

        if index.isValid():
            if role == QtCore.Qt.EditRole:

                item = index.internalPointer()
                column = index.column()
                key = self.COLUMNS[column]
                item[key] = value

                # passing `list()` for PyQt5 (see PYSIDE-462)
                self.dataChanged.emit(index, index, list())

                # must return true if successful
                return True

        return False

    def setColumns(self, keys):
        assert isinstance(keys, (list, tuple))
        self.COLUMNS = keys

    def headerData(self, section, orientation, role):

        if role == QtCore.Qt.DisplayRole:
            if section < len(self.COLUMNS):
                return self.COLUMNS[section]

        super(TreeModel, self).headerData(section, orientation, role)

    def flags(self, index):
        return (
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsSelectable
        )

    def parent(self, index):

        item = index.internalPointer()
        parent_item = item.parent()

        # If it has no parents we return invalid
        if parent_item == self._root_item or not parent_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def index(self, row, column, parent):
        """Return index for row/column under parent"""

        if not parent.isValid():
            parentItem = self._root_item
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def add_child(self, item, parent=None):
        if parent is None:
            parent = self._root_item

        parent.add_child(item)

    def column_name(self, column):
        """Return column key by index"""

        if column < len(self.COLUMNS):
            return self.COLUMNS[column]

    def clear(self):
        self.beginResetModel()
        self._root_item = Item()
        self.endResetModel()
