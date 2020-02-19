import logging

from ...vendor.Qt import QtCore
from ..models import TreeModel
from .. import delegates as tools_delegates
from .. import lib

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

        # Current value of the index
        value = index.data(QtCore.Qt.DisplayRole)

        # Add all available versions to the editor
        item = index.data(TreeModel.ItemRole)
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

        index = None
        for i, version in enumerate(versions):
            if (
                master_version and
                doc_for_master_version is None and
                master_version["version_id"] == version["_id"]
            ):
                doc_for_master_version = version

            label = lib.format_version(version["name"])
            editor.addItem(label, userData=version)

            if version["name"] == value:
                index = i

        if master_version and doc_for_master_version:
            label = lib.format_version(
                doc_for_master_version["name"], True
            )
            if label == value:
                index = len(versions)
            master_version["data"] = doc_for_master_version["data"]
            master_version["name"] = lib.MasterVersionType(
                doc_for_master_version["name"]
            )
            editor.addItem(label, userData=master_version)

        if index is None:
            index = len(versions)
            if not (master_version and doc_for_master_version):
                index -= 1

        editor.setCurrentIndex(index)  # Will trigger index-change signal
        self.first_run = False
        self.lock = True
