import time
from datetime import datetime
import logging
import numbers

from ..vendor.Qt import QtWidgets, QtCore, QtGui
from .. import io
from . import lib
from ..lib import MasterVersionType
from .models import TreeModel

log = logging.getLogger(__name__)


class VersionDelegate(QtWidgets.QStyledItemDelegate):
    """A delegate that display version integer formatted as version string."""

    version_changed = QtCore.Signal()
    first_run = False
    lock = False

    def displayText(self, value, locale):
        if isinstance(value, MasterVersionType):
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
        if item["version_document"]["type"] != "master_version":
            assert isinstance(value, numbers.Integral), (
                "Version is not integer"
            )

        # Add all available versions to the editor
        parent_id = item["version_document"]["parent"]
        versions = list(io.find(
            {
                "type": "version",
                "parent": parent_id
            },
            sort=[("name", 1)]
        ))

        master_version = io.find_one({
            "type": "master_version",
            "parent": parent_id
        })

        doc_for_master_version = None

        selected = None
        items = []
        for version in versions:
            version_tags = version["data"].get("tags") or []
            if "deleted" in version_tags:
                continue

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
            item.setData(master_version, QtCore.Qt.UserRole)
            items.append(item)

        # Reverse items so latest versions be upper
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

    def setModelData(self, editor, model, index):
        """Apply the integer version back in the model"""
        version = editor.itemData(editor.currentIndex())
        model.setData(index, version["name"])


def pretty_date(t, now=None, strftime="%b %d %Y %H:%M"):
    """Parse datetime to readable timestamp

    Within first ten seconds:
        - "just now",
    Within first minute ago:
        - "%S seconds ago"
    Within one hour ago:
        - "%M minutes ago".
    Within one day ago:
        - "%H:%M hours ago"
    Else:
        "%Y-%m-%d %H:%M:%S"

    """

    assert isinstance(t, datetime)
    if now is None:
        now = datetime.now()
    assert isinstance(now, datetime)
    diff = now - t

    second_diff = diff.seconds
    day_diff = diff.days

    # future (consider as just now)
    if day_diff < 0:
        return "just now"

    # history
    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 86400:
            minutes = (second_diff % 3600) // 60
            hours = second_diff // 3600
            return "{0}:{1:02d} hours ago".format(hours, minutes)

    return t.strftime(strftime)


def pretty_timestamp(t, now=None):
    """Parse timestamp to user readable format

    >>> pretty_timestamp("20170614T151122Z", now="20170614T151123Z")
    'just now'

    >>> pretty_timestamp("20170614T151122Z", now="20170614T171222Z")
    '2:01 hours ago'

    Args:
        t (str): The time string to parse.
        now (str, optional)

    Returns:
        str: human readable "recent" date.

    """

    if now is not None:
        try:
            now = time.strptime(now, "%Y%m%dT%H%M%SZ")
            now = datetime.fromtimestamp(time.mktime(now))
        except ValueError as e:
            log.warning("Can't parse 'now' time format: {0} {1}".format(t, e))
            return None

    if isinstance(t, float):
        dt = datetime.fromtimestamp(t)
    else:
        # Parse the time format as if it is `str` result from
        # `pyblish.lib.time()` which usually is stored in Avalon database.
        try:
            t = time.strptime(t, "%Y%m%dT%H%M%SZ")
        except ValueError as e:
            log.warning("Can't parse time format: {0} {1}".format(t, e))
            return None
        dt = datetime.fromtimestamp(time.mktime(t))

    # prettify
    return pretty_date(dt, now=now)


class PrettyTimeDelegate(QtWidgets.QStyledItemDelegate):
    """A delegate that displays a timestamp as a pretty date.

    This displays dates like `pretty_date`.

    """

    def displayText(self, value, locale):

        if value is None:
            # Ignore None value
            return

        return pretty_timestamp(value)
