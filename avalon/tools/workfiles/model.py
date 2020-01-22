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
