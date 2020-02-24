import os
import logging

from ... import style
from ...vendor.Qt import QtCore
from ...vendor import qtawesome

from ..models import TreeModel, Item

log = logging.getLogger(__name__)


class FilesModel(TreeModel):
    """Model listing files with specified extensions in a root folder"""
    Columns = ["filename", "date"]

    FileNameRole = QtCore.Qt.UserRole + 2
    DateModifiedRole = QtCore.Qt.UserRole + 3
    FilePathRole = QtCore.Qt.UserRole + 4
    IsEnabled = QtCore.Qt.UserRole + 5

    def __init__(self, file_extensions, parent=None):
        super(FilesModel, self).__init__(parent=parent)

        self._root = None
        self._file_extensions = file_extensions
        self._icons = {"file": qtawesome.icon("fa.file-o",
                                              color=style.colors.default)}

    def set_root(self, root):
        self._root = root
        self.refresh()

    def _add_empty(self):

        item = Item()
        item.update({
            # Put a display message in 'filename'
            "filename": "No files found.",
            # Not-selectable
            "enabled": False,
            "filepath": None
        })

        self.add_child(item)

    def refresh(self):

        self.clear()
        self.beginResetModel()

        root = self._root

        if not root:
            self.endResetModel()
            return

        if not os.path.exists(root):
            # Add Work Area does not exist placeholder
            log.debug("Work Area does not exist: %s", root)
            message = "Work Area does not exist. Use Save As to create it."
            item = Item({
                "filename": message,
                "date": None,
                "filepath": None,
                "enabled": False,
                "icon": qtawesome.icon("fa.times",
                                       color=style.colors.mid)
            })
            self.add_child(item)
            self.endResetModel()
            return

        extensions = self._file_extensions

        for f in os.listdir(root):
            path = os.path.join(root, f)
            if os.path.isdir(path):
                continue

            if extensions and os.path.splitext(f)[1] not in extensions:
                continue

            modified = os.path.getmtime(path)

            item = Item({
                "filename": f,
                "date": modified,
                "filepath": path
            })

            self.add_child(item)

        self.endResetModel()

    def data(self, index, role):

        if not index.isValid():
            return

        if role == QtCore.Qt.DecorationRole:
            # Add icon to filename column
            item = index.internalPointer()
            if index.column() == 0:
                if item["filepath"]:
                    return self._icons["file"]
                else:
                    return item.get("icon", None)
        if role == self.FileNameRole:
            item = index.internalPointer()
            return item["filename"]
        if role == self.DateModifiedRole:
            item = index.internalPointer()
            return item["date"]
        if role == self.FilePathRole:
            item = index.internalPointer()
            return item["filepath"]
        if role == self.IsEnabled:
            item = index.internalPointer()
            return item.get("enabled", True)

        return super(FilesModel, self).data(index, role)

    def headerData(self, section, orientation, role):

        # Show nice labels in the header
        if role == QtCore.Qt.DisplayRole and \
                orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Date modified"

        return super(FilesModel, self).headerData(section, orientation, role)
