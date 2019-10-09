from ..vendor.Qt import QtWidgets, QtCore
from .. import io

from .models import TreeModel


class VersionDelegate(QtWidgets.QStyledItemDelegate):
    """A delegate that display version integer formatted as version string."""

    version_changed = QtCore.Signal()
    first_run = False
    lock = False

    def _format_version(self, value):
        """Formats integer to displayable version name"""
        return "v{0:03d}".format(value)

    def displayText(self, value, locale):
        assert isinstance(value, int), "Version is not `int`"
        return self._format_version(value)

    def createEditor(self, parent, option, index):
        item = index.data(TreeModel.ItemRole)
        if item.get("isGroup"):
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
        assert isinstance(value, int), "Version is not `int`"

        # Add all available versions to the editor
        item = index.data(TreeModel.ItemRole)
        parent_id = item["version_document"]["parent"]
        versions = io.find({"type": "version", "parent": parent_id},
                           sort=[("name", 1)])
        index = 0
        for i, version in enumerate(versions):
            label = self._format_version(version["name"])
            editor.addItem(label, userData=version)

            if version["name"] == value:
                index = i

        editor.setCurrentIndex(index)  # Will trigger index-change signal
        self.first_run = False
        self.lock = True

    def setModelData(self, editor, model, index):
        """Apply the integer version back in the model"""
        version = editor.itemData(editor.currentIndex())
        model.setData(index, version["name"])
