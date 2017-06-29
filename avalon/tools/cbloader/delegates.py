import time
from datetime import datetime
import logging

from ...vendor.Qt import QtWidgets, QtCore
from ... import io
from .model import SubsetsModel

log = logging.getLogger(__name__)


def pretty_date(t, now=None):
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
        now = datetime.utcnow()
    assert isinstance(now, datetime)
    diff = now - t

    second_diff = diff.seconds
    day_diff = diff.days

    # future (consider as just now)
    if day_diff < 0:
        return 'just now'

    # history
    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 86400:
            minutes = (second_diff % 3600) / 60
            hours = second_diff / 3600
            return "{0}:{1:02d} hours ago".format(hours, minutes)

    return t.strftime("%Y-%m-%d %H:%M:%S")


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
        except ValueError, e:
            log.warning("Can't parse 'now' time format: {0} {1}".format(t, e))
            return None

    try:
        t = time.strptime(t, "%Y%m%dT%H%M%SZ")
    except ValueError, e:
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
        return pretty_timestamp(value)


class VersionDelegate(QtWidgets.QStyledItemDelegate):
    """A delegate that display version integer formatted as version string.
    
    """

    def _format_version(self, value):
        """Formats integer to displayable version name"""
        # todo(roy): formatting of version should be configurable
        return "v{0:03d}".format(value)

    def displayText(self, value, locale):
        assert isinstance(value, int), "Version is not `int`"
        return self._format_version(value)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        return editor

    def setEditorData(self, editor, index):

        editor.clear()

        # Current value of the index
        value = index.data(QtCore.Qt.DisplayRole)
        assert isinstance(value, int), "Version is not `int`"

        # Add all available versions to the editor
        node = index.data(SubsetsModel.NodeRole)
        parent_id = node['version_document']['parent']
        versions = io.find({"type": "version", "parent": parent_id},
                           sort=[("name", 1)])
        index = 0
        for i, version in enumerate(versions):
            label = self._format_version(version['name'])
            editor.addItem(label, userData=version)

            if version['name'] == value:
                index = i

        editor.setCurrentIndex(index)

    def setModelData(self, editor, model, index):
        """Apply the integer version back in the model"""
        version = editor.itemData(editor.currentIndex())
        model.set_version(index, version)
