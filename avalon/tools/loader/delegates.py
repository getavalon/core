import time
from datetime import datetime
import logging

from ...vendor.Qt import QtWidgets

log = logging.getLogger(__name__)


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
        return pretty_timestamp(value)
