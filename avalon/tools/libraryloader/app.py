import sys
import time

from .io_nonsingleton import DbConnector
from ...vendor.Qt import QtWidgets, QtCore
from ... import style
from .. import lib
from .lib import refresh_family_config, find_config
from .widgets import (
    SubsetWidget,
    VersionWidget,
    FamilyListWidget,
    AssetWidget,
    AssetModel,
    ProjectsWidget
)

module = sys.modules[__name__]
module.window = None

# Custom roles
DocumentRole = AssetModel.DocumentRole


class Window(QtWidgets.QDialog):
    """Asset loader interface"""

    tool_name = "Library Loader 0.5"
    signal_project_changed = QtCore.Signal(object)

    def __init__(self, parent=None, icon=None):
        super(Window, self).__init__(parent)

        # Enable minimize and maximize for app
        self.setWindowTitle(self.tool_name)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        if icon is not None:
            self.setWindowIcon(icon)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()
        footer.setFixedHeight(20)

        container = QtWidgets.QWidget()
        self._db = DbConnector()
        self.project_widget = ProjectsWidget(parent=self)

        assets = AssetWidget(self)
        families = FamilyListWidget(self)
        subsets = SubsetWidget(self)
        version = VersionWidget(self)

        change_project = QtWidgets.QPushButton("Change Project")

        # Create splitter to show / hide family filters
        asset_filter_splitter = QtWidgets.QSplitter()
        asset_filter_splitter.setOrientation(QtCore.Qt.Vertical)
        asset_filter_splitter.addWidget(assets)
        asset_filter_splitter.addWidget(families)
        asset_filter_splitter.setStretchFactor(0, 65)
        asset_filter_splitter.setStretchFactor(1, 35)

        version_project = QtWidgets.QSplitter()
        version_project.setOrientation(QtCore.Qt.Vertical)
        version_project.addWidget(version)
        version_project.addWidget(change_project)
        version_project.setStretchFactor(0, 95)
        version_project.setStretchFactor(1, 5)

        container_layout = QtWidgets.QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        split = QtWidgets.QSplitter()
        split.addWidget(asset_filter_splitter)
        split.addWidget(subsets)
        split.addWidget(version_project)
        # split.addWidget(version)
        split.setSizes([180, 950, 200])
        container_layout.addWidget(split)

        body_layout = QtWidgets.QHBoxLayout(body)
        body_layout.addWidget(container)
        body_layout.setContentsMargins(0, 0, 0, 0)

        message = QtWidgets.QLabel()
        message.hide()

        footer_layout = QtWidgets.QVBoxLayout(footer)
        footer_layout.addWidget(message)
        footer_layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.data = {
            "widgets": {"families": families},
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

        families.active_changed.connect(subsets.set_family_filters)
        assets.selection_changed.connect(self.on_assetschanged)
        subsets.active_changed.connect(self.on_subsetschanged)
        subsets.version_changed.connect(self.on_versionschanged)
        change_project.clicked.connect(self.show_projects_widget)
        self.signal_project_changed.connect(self.on_projectchanged)

        # Defaults
        self.resize(1330, 700)
        self.show_projects_widget()

    def show_projects_widget(self):
        self.project_widget.show()

    @property
    def current_project(self):
        if self.db.active_project() == '':
            return None
        return self.db.active_project()

    def on_projectchanged(self, project_name):
        self.db.activate_project(project_name)
        refresh_family_config(self.db)

        # Find the set config
        _config = find_config(self.db)
        if hasattr(_config, "install"):
            _config.install()
        else:
            print("Config `%s` has no function `install`" %
                  _config.__name__)

        self._refresh()
        self._assetschanged()

        self.setWindowTitle(
            "{} - {}/{}".format(
                self.tool_name,
                self.db.registered_root(),
                self.db.session.get("AVALON_PROJECT", "No project selected")))

    @property
    def db(self):
        return self._db

    # -------------------------------
    # Delay calling blocking methods
    # -------------------------------

    def refresh(self):
        self.echo("Fetching results..")
        lib.schedule(self._refresh, 50, channel="mongo")

    def on_assetschanged(self, *args):
        self.echo("Fetching asset..")
        lib.schedule(self._assetschanged, 50, channel="mongo")

    def on_subsetschanged(self, *args):
        self.echo("Fetching subset..")
        lib.schedule(self._versionschanged, 50, channel="mongo")

    def on_versionschanged(self, *args):
        self.echo("Fetching version..")
        lib.schedule(self._versionschanged, 150, channel="mongo")

    # ------------------------------

    def _refresh(self):
        """Load assets from database"""

        # Ensure a project is loaded
        project = self.db.find_one({"type": "project"})
        assert project, "This is a bug"

        assets_model = self.data["model"]["assets"]
        assets_model.refresh()
        assets_model.setFocus()

        families = self.data["widgets"]["families"]
        families.refresh()

        # Update state
        state = self.data["state"]
        state["template"] = project["config"]["template"]["publish"]
        state["context"]["root"] = self.db.registered_root()
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
            type = "asset"
            silo = assets_model.get_current_silo()
            if len(silo) == 0:
                return
            document = self.db.find_one({
                "type": type,
                "name": silo
            })

        else:
            document = asset_item.data(DocumentRole)

        if document is None:
            return
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
        selection = subsets.view.selectionModel()

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

        # self.db.uninstall()

        print("Good bye")
        return super(Window, self).closeEvent(event)


def show(debug=False, parent=None, use_context=False, icon=None):
    """Display Loader GUI

    Arguments:
        debug (bool, optional): Run loader in debug-mode,
            defaults to False
        parent (QtCore.QObject, optional): The Qt object to parent to.
        use_context (bool): Whether to apply the current context upon launch

    """
    # Remember window
    if module.window is not None:
        try:
            module.window.show()

            # If the window is minimized then unminimize it.
            if module.window.windowState() & QtCore.Qt.WindowMinimized:
                module.window.setWindowState(QtCore.Qt.WindowActive)

            # Raise and activate the window
            module.window.raise_()             # for MacOS
            module.window.activateWindow()     # for Windows
            module.window.refresh()
            return
        except RuntimeError as e:
            if not e.message.rstrip().endswith("already deleted."):
                raise

            # Garbage collected
            module.window = None

    if debug:
        import traceback
        sys.excepthook = lambda typ, val, tb: traceback.print_last()

    with lib.application():
        window = Window(parent, icon)
        window.setStyleSheet(style.load_stylesheet())
        window.show()

        module.window = window


def cli(args):

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project")

    show()
