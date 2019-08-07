from ...vendor.Qt import QtWidgets
from .. import VersionTextEdit


class VersionWidget(QtWidgets.QWidget):
    """A Widget that display information about a specific version"""
    def __init__(self, parent=None):
        super(VersionWidget, self).__init__(parent=parent)

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Version")
        data = VersionTextEdit()
        data.setReadOnly(True)
        layout.addWidget(label)
        layout.addWidget(data)

        self.data = data

    def set_version(self, version_id):
        self.data.set_version(version_id)
