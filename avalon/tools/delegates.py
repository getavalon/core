import numbers

from ..vendor.Qt import QtWidgets, QtCore
from .. import io
from . import lib
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

    def displayText(self, value, locale):
        if isinstance(value, lib.MasterVersionType):
            return lib.format_version(value, True)
        assert isinstance(value, numbers.Integral), (
            "Version is not integer. \"{}\" {}".format(value, str(type(value)))
        )
        return lib.format_version(value)

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
        item = index.data(TreeModel.ItemRole)
        value = index.data(QtCore.Qt.DisplayRole)
        if item["version_document"]["type"] == "version":
            assert isinstance(value, numbers.Integral), (
                "Version is not integer"
            )

        # Add all available versions to the editor
        parent_id = item["version_document"]["parent"]
        versions = io.find(
            {
                "type": "version",
                "parent": parent_id
            },
            sort=[("name", 1)]
        )

        master_version = io.find({
            "type": "master_version",
            "parent": parent_id
        })
        doc_for_master_version = None

        index = 0
        for i, version in enumerate(versions):
            if (
                master_version and
                doc_for_master_version is None and
                version["_id"] == master_version["version_id"]
            ):
                doc_for_master_version = version

            label = lib.format_version(version["name"])
            editor.addItem(label, userData=version)

            if version["name"] == value:
                index = i

        if master_version and doc_for_master_version:
            version_name = doc_for_master_version["name"]

            master_version["name"] = version_name
            print("setEditorData", version_name)
            label = lib.format_version(version_name, True)

            editor.addItem(label, userData=master_version)

        editor.setCurrentIndex(index)  # Will trigger index-change signal
        self.first_run = False
        self.lock = True

    def setModelData(self, editor, model, index):
        """Apply the integer version back in the model"""
        version = editor.itemData(editor.currentIndex())
        value = version["name"]
        model.setData(index, value)
