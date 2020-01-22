from ...vendor.Qt import QtCore

from ..models import TreeModel, Item


class WorkFileItem(Item):
    def sort(self, key, order):
        children = sorted(self.children(), key=lambda item: item[key])
        if order == QtCore.Qt.DescendingOrder:
            children = reversed(children)

        self._children = list(children)
        for child in self._children:
            child.sort(key, order)


class WorkFileModel(TreeModel):
    """A model listing the tasks combined for a list of assets"""

    Columns = ["Filename", "Modified"]
    FilenameRole = QtCore.Qt.UserRole + 2
    ModifiedRole = QtCore.Qt.UserRole + 3
    item_class = WorkFileItem

    def parent(self, index):
        item = index.internalPointer()
        if isinstance(item, int):
            index = self.createIndex(item, 0, self._root_item)
        return super(WorkFileModel, self).parent(index)

    def sort(self, column, order):
        # Use super of QAbstractItemModel because in PySide `parent` method
        # does not return parent QObject but tries to find Item parent
        parent = super(QtCore.QAbstractItemModel, self).parent()
        selection = []
        if parent and hasattr(parent, "selectionModel"):
            selection_model = parent.selectionModel()
            for row in selection_model.selectedRows():
                selection.append(row.data(self.ItemRole))

        self.beginResetModel()

        key = self.Columns[column]
        self._root_item.sort(key, order)

        self.endResetModel()

        if not parent or not selection:
            return

        item_selection = QtCore.QItemSelection()
        for idx, item in enumerate(self._root_item.children()):
            if item not in selection:
                continue

            index = self.createIndex(idx, 0, idx)
            item_selection.append(QtCore.QItemSelectionRange(index))

        selection_model.select(
            item_selection,
            (
                QtCore.QItemSelectionModel.SelectCurrent |
                QtCore.QItemSelectionModel.Rows
            )
        )

    def add_file(self, filename, modified=None):
        self.beginResetModel()

        if not modified:
            modified = "< unknown >"

        item = self.ItemClass({
            "Filename": filename,
            "Modified": modified
        })
        self.add_child(item)

        self.endResetModel()

    def data(self, index, role):
        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            if index.column() == 0:
                role = self.FilenameRole
            elif index.column() == 1:
                role = self.ModifiedRole

        item = super(WorkFileModel, self).data(index, self.ItemRole)
        if role == self.ItemRole:
            return item

        elif role == self.FilenameRole:
            return item["Filename"]

        elif role == self.ModifiedRole:
            return item["Modified"]

        return super(WorkFileModel, self).data(index, role)
