import os
import sys
import time

from ..projectmanager.widget import AssetWidget, AssetModel
from ...vendor.Qt import QtWidgets, QtCore, QtGui
from ... import api, io
from .. import lib
from .widgets import SubsetWidget, VersionWidget

module = sys.modules[__name__]
module.window = None

# Custom roles
DocumentRole = AssetModel.DocumentRole


class Window(QtWidgets.QDialog):
    """Asset loader interface"""

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle(
            "Asset Loader 2.0 - %s/%s" % (
                api.registered_root(),
                os.getenv("AVALON_PROJECT")))

        # Enable minimize and maximize for app
        self.setWindowFlags(QtCore.Qt.Window)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()
        footer.setFixedHeight(20)

        container = QtWidgets.QWidget()

        assets = AssetWidget()
        subsets = SubsetWidget()
        version = VersionWidget()

        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        split = QtWidgets.QSplitter()
        split.addWidget(assets)
        split.addWidget(subsets)
        split.addWidget(version)
        split.setStretchFactor(0, 30)
        split.setStretchFactor(1, 90)
        split.setStretchFactor(2, 30)
        layout.addWidget(split)

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)

        message = QtWidgets.QLabel()
        message.hide()

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(message)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.data = {
            "model": {
                "assets": assets,
                "subsets": subsets,
                "version": version,
            },
            "label": {
                "message": message,
            },
            "state": {
                "template": None,
                "locations": list(),
                "context": {
                    "root": None,
                    "project": None,
                    "asset": None,
                    "silo": None,
                    "subset": None,
                    "version": None,
                    "representation": None,
                },
            }
        }

        assets.selection_changed.connect(self.on_assetschanged)
        subsets.active_changed.connect(self.on_versionschanged)

        # Defaults
        self.resize(1200, 600)

    # -------------------------------
    # Delay calling blocking methods
    # -------------------------------

    def refresh(self):
        self.echo("Fetching results..")
        lib.schedule(self._refresh, 100, channel="mongo")

    def on_assetschanged(self, *args):
        self.echo("Fetching results..")
        lib.schedule(self._assetschanged, 100, channel="mongo")

    def on_versionschanged(self, *args):
        self.echo("Fetching results..")
        lib.schedule(self._versionschanged, 100, channel="mongo")

    # ------------------------------

    def _refresh(self):
        """Load assets from database"""

        # Ensure a project is loaded
        project = io.find_one({"type": "project"})
        assert project, "This is a bug"

        assets_model = self.data["model"]["assets"]
        assets_model.refresh()
        assets_model.setFocus()

        # Update state
        state = self.data["state"]
        state["template"] = project["config"]["template"]["publish"]
        state["context"]["root"] = api.registered_root()
        state["context"]["project"] = project["name"]

    def _assetschanged(self):
        """Selected assets have changed"""

        assets_model = self.data["model"]["assets"]
        subsets = self.data["model"]["subsets"]
        subsets_model = subsets.model
        subsets_model.clear()

        t1 = time.time()

        asset_item = assets_model.get_active_index()
        if asset_item is None or not asset_item.isValid():
            return

        document = asset_item.data(DocumentRole)
        subsets_model.set_asset(document['_id'])

        # Enforce the columns to fit the data (purely cosmetic)
        rows = subsets_model.rowCount(QtCore.QModelIndex())
        for i in range(rows):
            subsets.view.resizeColumnToContents(i)

        # Clear the version information on asset change
        self.data['model']['version'].set_version(None)

        self.data["state"]["context"]["asset"] = document["name"]
        self.data["state"]["context"]["silo"] = document["silo"]
        self.echo("Duration: %.3fs" % (time.time() - t1))

    def _versionschanged(self):

        subsets = self.data["model"]["subsets"]
        selection = subsets.selectionModel()

        # Active must be in the selected rows otherwise we
        # assume it's not actually an "active" current index.
        version = None
        active = selection.currentIndex()
        if active:
            rows = selection.selectedRows(column=active.column())
            if active in rows:
                node = active.data(subsets.model.NodeRole)
                version = node['version_document']['_id']

        self.data['model']['version'].set_version(version)

    def echo(self, message):
        widget = self.data["label"]["message"]
        widget.setText(str(message))
        widget.show()
        print(message)

        lib.schedule(widget.hide, 5000, channel="message")

    def closeEvent(self, event):
        # Kill on holding SHIFT
        modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
        shift_pressed = QtCore.Qt.ShiftModifier & modifiers

        if shift_pressed:
            print("Force quitted..")
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Kill on holding SHIFT
        modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
        shift_pressed = QtCore.Qt.ShiftModifier & modifiers

        if shift_pressed:
            print("Force quitted..")
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        print("Good bye")
        return super(Window, self).closeEvent(event)


def show(root=None, debug=False, parent=None):
    """Display Loader GUI

    Arguments:
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    # Remember window
    if module.window is not None:
        try:
            return module.window.show()
        except RuntimeError as e:
            if not e.message.rstrip().endswith("already deleted."):
                raise

            # Garbage collected
            module.window = None

    if debug:
        import traceback
        sys.excepthook = lambda typ, val, tb: traceback.print_last()

        io.install()

        any_project = next(
            project for project in io.projects()
            if project.get("active", True) is not False
        )

        api.Session["AVALON_PROJECT"] = any_project["name"]
        module.project = any_project["name"]

    with lib.application():
        window = Window(parent)
        window.show()

        window.refresh()

        module.window = window
