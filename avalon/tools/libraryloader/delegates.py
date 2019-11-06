import time
from datetime import datetime
import logging

from ...vendor.Qt import QtWidgets, QtCore
from ..models import TreeModel
from .. import delegates as tools_delegates

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
        assert isinstance(value, int), "Version is not `int`"

        # Add all available versions to the editor
        item = index.data(TreeModel.ItemRole)
        parent_id = item["version_document"]["parent"]
        versions = self.dbcon.find(
            {"type": "version", "parent": parent_id},
            sort=[("name", 1)]
        )
        index = 0
        for i, version in enumerate(versions):
            label = self._format_version(version["name"])
            editor.addItem(label, userData=version)

            if version["name"] == value:
                index = i

        editor.setCurrentIndex(index)  # Will trigger index-change signal
        self.first_run = False
        self.lock = True
