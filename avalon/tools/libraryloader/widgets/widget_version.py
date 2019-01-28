import datetime
import pprint
from ....vendor.Qt import QtWidgets


class VersionWidget(QtWidgets.QWidget):
    """A Widget that display information about a specific version"""
    def __init__(self, parent=None):
        super(VersionWidget, self).__init__(parent=parent)
        self.db = parent.db
        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Version")
        data = VersionTextEdit(self)
        data.setReadOnly(True)
        layout.addWidget(label)
        layout.addWidget(data)

        self.data = data

    def set_version(self, version_id):
        self.data.set_version(version_id)


class VersionTextEdit(QtWidgets.QTextEdit):
    """QTextEdit that displays version specific information.

    This also overrides the context menu to add actions like copying
    source path to clipboard or copying the raw data of the version
    to clipboard.

    """
    def __init__(self, parent=None):
        super(VersionTextEdit, self).__init__(parent=parent)
        self.db = parent.db
        self.data = {
            "source": None,
            "raw": None
        }

        # Reset
        self.set_version(None)

    def set_version(self, version_id):

        if not version_id:
            # Reset state to empty
            self.data = {
                "source": None,
                "raw": None,
            }
            self.setText("")
            self.setEnabled(True)
            return

        self.setEnabled(True)

        print("Querying..")

        version = self.db.find_one(
            {"_id": version_id, "type": "version"}
        )
        assert version, "Not a valid version id"

        subset = self.db.find_one(
            {"_id": version['parent'], "type": "subset"}
        )
        assert subset, "No valid subset parent for version"

        # Define readable creation timestamp
        created = version["data"]["time"]
        created = datetime.datetime.strptime(created, "%Y%m%dT%H%M%SZ")
        created = datetime.datetime.strftime(created, "%b %d %Y %H:%M")

        comment = version['data'].get("comment", None) or "No comment"

        source = version['data'].get("source", None)
        source_label = source if source else "No source"

        # Store source and raw data
        self.data['source'] = source
        self.data['raw'] = version

        data = {
            "subset": subset['name'],
            "version": version['name'],
            "comment": comment,
            "created": created,
            "source": source_label
        }

        self.setHtml(u"""
<h3>{subset} v{version:03d}</h3>
<b>Comment</b><br>
{comment}<br>
<br>
<b>Created</b><br>
{created}<br>
<br>
<b>Source</b><br>
{source}<br>""".format(**data))

    def contextMenuEvent(self, event):
        """Context menu with additional actions"""
        menu = self.createStandardContextMenu()

        # Add additional actions when any text so we can assume
        # the version is set.
        if self.toPlainText().strip():

            menu.addSeparator()
            action = QtWidgets.QAction("Copy source path to clipboard",
                                       menu)
            action.triggered.connect(self.on_copy_source)
            menu.addAction(action)

            action = QtWidgets.QAction("Copy raw data to clipboard",
                                       menu)
            action.triggered.connect(self.on_copy_raw)
            menu.addAction(action)

        menu.exec_(event.globalPos())
        del menu

    def on_copy_source(self):
        """Copy formatted source path to clipboard"""
        source = self.data.get("source", None)
        if not source:
            return

        path = source.format(root=self.db.registered_root())
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(path)

    def on_copy_raw(self):
        """Copy raw version data to clipboard

        The data is string formatted with `pprint.pformat`.

        """
        raw = self.data.get("raw", None)
        if not raw:
            return

        raw_text = pprint.pformat(raw)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(raw_text)
