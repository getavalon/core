import numbers

from ..vendor.Qt import QtWidgets, QtCore
from .. import io

from .models import TreeModel

try:
    long
except NameError:
    long = int


class VersionDelegate(QtWidgets.QStyledItemDelegate):
    """A delegate that display version integer formatted as version string."""

    version_changed = QtCore.Signal()
    first_run = False
    lock = False

    def _format_version(self, value):
        """Formats integer to displayable version name"""
        return "v{0:03d}".format(value)

    def displayText(self, value, locale):
        assert isinstance(value, numbers.Integral), "Version is not integer"
        return self._format_version(value)

    def createEditor(self, parent, option, index):
        item = index.data(TreeModel.ItemRole)
        if item.get("isGroup") or item.get("isMerged"):
            return

        editor = QtWidgets.QComboBox(parent)

        def commit_data():
            if not self.first_run:
                self.commitData.emit(editor)  # Update model data
                self.version_changed.emit()   # Display model data
        editor.currentIndexChanged.connect(commit_data)

        self.first_run = True
        self.lock = False

        return editor

    def setEditorData(self, editor, index):
        if self.lock:
            # Only set editor data once per delegation
            return

        editor.clear()

        # Current value of the index
        value = index.data(QtCore.Qt.DisplayRole)
        assert isinstance(value, numbers.Integral), "Version is not integer"

        # Add all available versions to the editor
        item = index.data(TreeModel.ItemRole)
        parent_id = item["version_document"]["parent"]
        versions = io.find({"type": "version", "parent": parent_id},
                           sort=[("name", 1)])
        index = 0
        enum_index = 0
        for version in versions:
            version_tags = version["data"].get("tags") or []
            if "deleted" in version_tags:
                continue

            label = self._format_version(version["name"])
            editor.addItem(label, userData=version)

            if version["name"] == value:
                index = enum_index

            enum_index += 1

        editor.setCurrentIndex(index)  # Will trigger index-change signal
        self.first_run = False
        self.lock = True

    def setModelData(self, editor, model, index):
        """Apply the integer version back in the model"""
        version = editor.itemData(editor.currentIndex())
        model.setData(index, version["name"])
