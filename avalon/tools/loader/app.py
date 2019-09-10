import sys
import time

from ...vendor.Qt import QtWidgets, QtCore
from ... import api, io, style

from ..models import AssetModel
from ..widgets import AssetWidget
from .. import lib

from .widgets import SubsetWidget, VersionWidget, FamilyListWidget

module = sys.modules[__name__]
module.window = None

# Custom roles
DocumentRole = AssetModel.DocumentRole


class Window(QtWidgets.QDialog):
    """Asset loader interface"""

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle(
            "Asset Loader 2.1 - %s/%s" % (
                api.registered_root(),
                api.Session.get("AVALON_PROJECT")))

        # Enable minimize and maximize for app
        self.setWindowFlags(QtCore.Qt.Window)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()
        footer.setFixedHeight(20)

        container = QtWidgets.QWidget()

        assets = AssetWidget(silo_creatable=False)
        families = FamilyListWidget()
        subsets = SubsetWidget()
        version = VersionWidget()

        # Create splitter to show / hide family filters
        asset_filter_splitter = QtWidgets.QSplitter()
        asset_filter_splitter.setOrientation(QtCore.Qt.Vertical)
        asset_filter_splitter.addWidget(assets)
        asset_filter_splitter.addWidget(families)
        asset_filter_splitter.setStretchFactor(0, 65)
        asset_filter_splitter.setStretchFactor(1, 35)

        container_layout = QtWidgets.QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        split = QtWidgets.QSplitter()
        split.addWidget(asset_filter_splitter)
        split.addWidget(subsets)
        split.addWidget(version)
        split.setSizes([180, 950, 200])

        # Remove QSplitter border
        split.setStyleSheet("QSplitter { border: 0px; }")

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
                    "assetId": None,
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

        # Defaults
        self.resize(1330, 700)

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

    def set_context(self, context, refresh=True):
        self.echo("Setting context: {}".format(context))
        lib.schedule(lambda: self._set_context(context, refresh=refresh),
                     50, channel="mongo")

    # ------------------------------

    def _refresh(self):
        """Load assets from database"""

        # Ensure a project is loaded
        project = io.find_one({"type": "project"})
        assert project, "This is a bug"

        assets_model = self.data["model"]["assets"]
        assets_model.refresh()
        assets_model.setFocus()

        families = self.data["widgets"]["families"]
        families.refresh()

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
        subsets_model.set_asset(document["_id"])

        # Clear the version information on asset change
        self.data["model"]["version"].set_version(None)

        self.data["state"]["context"]["asset"] = document["name"]
        self.data["state"]["context"]["assetId"] = document["_id"]
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
                node = active.data(subsets.model.ItemRole)
                if node is not None and not node.get("isGroup"):
                    version = node["version_document"]["_id"]

        self.data["model"]["version"].set_version(version)

    def _set_context(self, context, refresh=True):
        """Set the selection in the interface using a context.

        The context must contain `silo` and `asset` data by name.

        Note: Prior to setting context ensure `refresh` is triggered so that
              the "silos" are listed correctly, aside from that setting the
              context will force a refresh further down because it changes
              the active silo and asset.

        Args:
            context (dict): The context to apply.

        Returns:
            None

        """

        silo = context.get("silo", None)
        if silo is None:
            return

        asset = context.get("asset", None)
        if asset is None:
            return

        if refresh:
            # Workaround:
            # Force a direct (non-scheduled) refresh prior to setting the
            # asset widget's silo and asset selection to ensure it's correctly
            # displaying the silo tabs. Calling `window.refresh()` and directly
            # `window.set_context()` the `set_context()` seems to override the
            # scheduled refresh and the silo tabs are not shown.
            self._refresh()

        asset_widget = self.data["model"]["assets"]
        asset_widget.set_silo(silo)
        asset_widget.select_assets([asset], expand=True)

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

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        ctrl_pressed = QtCore.Qt.ControlModifier & modifiers

        # Grouping subsets on pressing Ctrl + G
        if (ctrl_pressed and event.key() == QtCore.Qt.Key_G and
                not event.isAutoRepeat()):
            self.show_grouping_dialog()
            return

        return super(Window, self).keyPressEvent(event)

    def show_grouping_dialog(self):
        subsets = self.data["model"]["subsets"]
        if not subsets.is_groupable():
            self.echo("Grouping not enabled.")
            return

        selected = subsets.selected_subsets()
        if not selected:
            self.echo("No selected subset.")
            return

        dialog = SubsetGroupingDialog(items=selected, parent=self)
        dialog.grouped.connect(self._assetschanged)
        dialog.show()


class SubsetGroupingDialog(QtWidgets.QDialog):

    grouped = QtCore.Signal()

    def __init__(self, items, parent=None):
        super(SubsetGroupingDialog, self).__init__(parent=parent)
        self.setWindowTitle("Grouping Subsets")
        self.setMinimumWidth(250)
        self.setModal(True)

        self.items = items
        self.subsets = parent.data["model"]["subsets"]
        self.asset_id = parent.data["state"]["context"]["assetId"]

        name = QtWidgets.QLineEdit()
        name.setPlaceholderText("Remain blank to ungroup..")

        # Menu for pre-defined subset groups
        name_button = QtWidgets.QPushButton()
        name_button.setFixedWidth(18)
        name_button.setFixedHeight(20)
        name_menu = QtWidgets.QMenu(name_button)
        name_button.setMenu(name_menu)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(name)
        name_layout.addWidget(name_button)
        name_layout.setContentsMargins(0, 0, 0, 0)

        group_btn = QtWidgets.QPushButton("Apply")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Group Name"))
        layout.addLayout(name_layout)
        layout.addWidget(group_btn)

        group_btn.clicked.connect(self.on_group)
        group_btn.setAutoDefault(True)
        group_btn.setDefault(True)

        self.name = name
        self.name_menu = name_menu

        self._build_menu()

    def _build_menu(self):
        menu = self.name_menu
        button = menu.parent()
        # Get and destroy the action group
        group = button.findChild(QtWidgets.QActionGroup)
        if group:
            group.deleteLater()

        active_groups = lib.get_active_group_config(self.asset_id,
                                                    include_predefined=True)
        # Build new action group
        group = QtWidgets.QActionGroup(button)
        for data in sorted(active_groups, key=lambda x: x["order"]):
            name = data["name"]
            icon = data["icon"]

            action = group.addAction(name)
            action.setIcon(icon)
            menu.addAction(action)

        group.triggered.connect(self._on_action_clicked)
        button.setEnabled(not menu.isEmpty())

    def _on_action_clicked(self, action):
        self.name.setText(action.text())

    def on_group(self):
        name = self.name.text().strip()
        self.subsets.group_subsets(name, self.asset_id, self.items)

        with lib.preserve_selection(tree_view=self.subsets.view,
                                    current_index=False):
            self.grouped.emit()
            self.close()


def show(debug=False, parent=None, use_context=False):
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

        io.install()

        any_project = next(
            project for project in io.projects()
            if project.get("active", True) is not False
        )

        api.Session["AVALON_PROJECT"] = any_project["name"]
        module.project = any_project["name"]

    with lib.application():

        # TODO: Global state, remove these
        lib.refresh_family_config_cache()
        lib.refresh_group_config_cache()

        window = Window(parent)
        window.setStyleSheet(style.load_stylesheet())
        window.show()

        if use_context:
            context = {"asset": api.Session["AVALON_ASSET"],
                       "silo": api.Session["AVALON_SILO"]}
            window.set_context(context, refresh=True)
        else:
            window.refresh()

        module.window = window


def cli(args):

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project")

    args = parser.parse_args(args)
    project = args.project

    io.install()

    # Store settings
    api.Session["AVALON_PROJECT"] = project

    from avalon import pipeline

    # Find the set config
    _config = pipeline.find_config()
    if hasattr(_config, "install"):
        _config.install()
    else:
        print("Config `%s` has no function `install`" %
              _config.__name__)

    show()
