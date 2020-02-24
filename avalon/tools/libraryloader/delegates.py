import logging
import numbers

from ...vendor.Qt import QtCore, QtGui
from ..models import TreeModel
from .. import delegates as tools_delegates
from .. import lib
from ...lib import MasterVersionType

log = logging.getLogger(__name__)


class VersionDelegate(tools_delegates.VersionDelegate):
    """A delegate that display version integer formatted as version string."""

    def __init__(self, dbcon, parent=None):
        self.dbcon = dbcon
        super(VersionDelegate, self).__init__(parent=parent)

    def setEditorData(self, editor, index):
        if self.lock:
            # Only set editor data once per delegation
            return

        editor.clear()

        item = index.data(TreeModel.ItemRole)
        # Current value of the index
        value = index.data(QtCore.Qt.DisplayRole)
        if item["version_document"]["type"] != "master_version":
            assert isinstance(value, numbers.Integral), (
                "Version is not integer"
            )

        # Add all available versions to the editor
        parent_id = item["version_document"]["parent"]
        versions = list(self.dbcon.find(
            {"type": "version", "parent": parent_id},
            sort=[("name", 1)]
        ))

        master_version = self.dbcon.find_one({
            "type": "master_version",
            "parent": parent_id
        })
        doc_for_master_version = None

        selected = None
        items = []
        for idx, version in enumerate(versions):
            if (
                master_version and
                doc_for_master_version is None and
                master_version["version_id"] == version["_id"]
            ):
                doc_for_master_version = version

            label = lib.format_version(version["name"])
            item = QtGui.QStandardItem(label)
            item.setData(version, QtCore.Qt.UserRole)
            items.append(item)

            if version["name"] == value:
                selected = item

        if master_version and doc_for_master_version:
            version_name = doc_for_master_version["name"]
            label = lib.format_version(version_name, True)
            if isinstance(value, MasterVersionType):
                index = len(versions)
            master_version["data"] = doc_for_master_version["data"]
            master_version["name"] = MasterVersionType(version_name)

            item = QtGui.QStandardItem(label)
            item.setBackground(QtGui.QColor(60, 60, 60))
            item.setData(master_version, QtCore.Qt.UserRole)
            items.append(item)

        items = list(reversed(items))
        for item in items:
            editor.model().appendRow(item)

        index = 0
        if selected:
            index = selected.row()

        # Will trigger index-change signal
        editor.setCurrentIndex(index)
        self.first_run = False
        self.lock = True
