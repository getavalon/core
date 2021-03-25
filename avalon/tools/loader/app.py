import sys
import time

from ...vendor.Qt import QtWidgets, QtCore
from ... import api, io, style

from ..models import AssetModel
from ..widgets import AssetWidget
from .. import lib

from .widgets import (
    SubsetWidget, VersionWidget, FamilyListWidget, ThumbnailWidget
)

module = sys.modules[__name__]
module.window = None

# Custom roles
DocumentRole = AssetModel.DocumentRole


class Window(QtWidgets.QDialog):
    """Asset loader interface"""

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle(
            "Asset Loader 2.1 - {}".format(api.Session.get("AVALON_PROJECT"))
        )

        # Groups config
        self.groups_config = lib.GroupsConfig(io)
        self.family_config_cache = lib.global_family_cache()

        # Enable minimize and maximize for app
        self.setWindowFlags(QtCore.Qt.Window)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()
        footer.setFixedHeight(20)

        container = QtWidgets.QWidget()

        assets = AssetWidget(io, multiselection=True, parent=self)
        families = FamilyListWidget(io, self.family_config_cache, self)
        subsets = SubsetWidget(
            io,
            self.groups_config,
            self.family_config_cache,
            parent=self
        )
        version = VersionWidget(io)
        thumbnail = ThumbnailWidget(io)

        thumb_ver_body = QtWidgets.QWidget()
        thumb_ver_layout = QtWidgets.QVBoxLayout(thumb_ver_body)
        thumb_ver_layout.setContentsMargins(0, 0, 0, 0)
        thumb_ver_layout.addWidget(thumbnail)
        thumb_ver_layout.addWidget(version)

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
        split.addWidget(thumb_ver_body)
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
            "widgets": {
                "families": families,
                "assets": assets,
                "subsets": subsets,
                "version": version,
                "thumbnail": thumbnail
            },
            "label": {
                "message": message,
            },
            "state": {
                "assetIds": None
            }
        }

        families.active_changed.connect(subsets.set_family_filters)
        assets.selection_changed.connect(self.on_assetschanged)
        assets.refresh_triggered.connect(self.on_assetschanged)
        assets.view.clicked.connect(self.on_assetview_click)
        subsets.active_changed.connect(self.on_subsetschanged)
        subsets.version_changed.connect(self.on_versionschanged)

        self.family_config_cache.refresh()
        self.groups_config.refresh()

        self._refresh()
        self._assetschanged()

        # Defaults
        self.resize(1330, 700)

    # -------------------------------
    # Delay calling blocking methods
    # -------------------------------

    def on_assetview_click(self, *args):
        subsets_widget = self.data["widgets"]["subsets"]
        selection_model = subsets_widget.view.selectionModel()
        if selection_model.selectedIndexes():
            selection_model.clearSelection()

    def refresh(self):
        self.echo("Fetching results..")
        lib.schedule(self._refresh, 50, channel="mongo")

    def on_assetschanged(self, *args):
        self.echo("Fetching asset..")
        lib.schedule(self._assetschanged, 50, channel="mongo")

    def on_subsetschanged(self, *args):
        self.echo("Fetching subset..")
        lib.schedule(self._subsetschanged, 50, channel="mongo")

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
        project = io.find_one({"type": "project"}, {"type": 1})
        assert project, "Project was not found! This is a bug"

        assets_widget = self.data["widgets"]["assets"]
        assets_widget.refresh()
        assets_widget.setFocus()

        families = self.data["widgets"]["families"]
        families.refresh()

    def clear_assets_underlines(self):
        """Clear colors from asset data to remove colored underlines
        When multiple assets are selected colored underlines mark which asset
        own selected subsets. These colors must be cleared from asset data
        on selection change so they match current selection.
        """
        last_asset_ids = self.data["state"]["assetIds"]
        if not last_asset_ids:
            return

        assets_widget = self.data["widgets"]["assets"]
        id_role = assets_widget.model.ObjectIdRole

        for index in lib.iter_model_rows(assets_widget.model, 0):
            if index.data(id_role) not in last_asset_ids:
                continue

            assets_widget.model.setData(
                index, [], assets_widget.model.subsetColorsRole
            )

    def _assetschanged(self):
        """Selected assets have changed"""
        t1 = time.time()

        assets_widget = self.data["widgets"]["assets"]
        subsets_widget = self.data["widgets"]["subsets"]
        subsets_model = subsets_widget.model

        subsets_model.clear()
        self.clear_assets_underlines()

        # filter None docs they are silo
        asset_docs = assets_widget.get_selected_assets()

        asset_ids = [asset_doc["_id"] for asset_doc in asset_docs]
        # Start loading
        subsets_widget.set_loading_state(
            loading=bool(asset_ids),
            empty=True
        )

        def on_refreshed(has_item):
            empty = not has_item
            subsets_widget.set_loading_state(loading=False, empty=empty)
            subsets_model.refreshed.disconnect()
            self.echo("Duration: %.3fs" % (time.time() - t1))

        subsets_model.refreshed.connect(on_refreshed)

        subsets_model.set_assets(asset_ids)
        subsets_widget.view.setColumnHidden(
            subsets_model.Columns.index("asset"),
            len(asset_ids) < 2
        )

        # Clear the version information on asset change
        self.data["widgets"]["version"].set_version(None)
        self.data["widgets"]["thumbnail"].set_thumbnail(asset_docs)

        self.data["state"]["assetIds"] = asset_ids

    def _subsetschanged(self):
        asset_ids = self.data["state"]["assetIds"]
        # Skip setting colors if not asset multiselection
        if not asset_ids or len(asset_ids) < 2:
            self._versionschanged()
            return

        subsets = self.data["widgets"]["subsets"]
        selected_subsets = subsets.selected_subsets(_merged=True, _other=False)

        asset_models = {}
        asset_ids = []
        for subset_node in selected_subsets:
            asset_ids.extend(subset_node.get("assetIds", []))
        asset_ids = set(asset_ids)

        for subset_node in selected_subsets:
            for asset_id in asset_ids:
                if asset_id not in asset_models:
                    asset_models[asset_id] = []

                color = None
                if asset_id in subset_node.get("assetIds", []):
                    color = subset_node["subsetColor"]

                asset_models[asset_id].append(color)

        self.clear_assets_underlines()

        assets_widget = self.data["widgets"]["assets"]
        indexes = assets_widget.view.selectionModel().selectedRows()

        for index in indexes:
            id = index.data(assets_widget.model.ObjectIdRole)
            if id not in asset_models:
                continue

            assets_widget.model.setData(
                index, asset_models[id], assets_widget.model.subsetColorsRole
            )
        # Trigger repaint
        assets_widget.view.updateGeometries()
        # Set version in Version Widget
        self._versionschanged()

    def _versionschanged(self):

        subsets = self.data["widgets"]["subsets"]
        selection = subsets.view.selectionModel()

        # Active must be in the selected rows otherwise we
        # assume it's not actually an "active" current index.
        version_docs = None
        version_doc = None
        active = selection.currentIndex()
        rows = selection.selectedRows(column=active.column())
        if active:
            if active in rows:
                item = active.data(subsets.model.ItemRole)
                if (
                    item is not None and
                    not (item.get("isGroup") or item.get("isMerged"))
                ):
                    version_doc = item["version_document"]

        if rows:
            version_docs = []
            for index in rows:
                if not index or not index.isValid():
                    continue
                item = index.data(subsets.model.ItemRole)
                if (
                    item is None
                    or item.get("isGroup")
                    or item.get("isMerged")
                ):
                    continue
                version_docs.append(item["version_document"])

        self.data["widgets"]["version"].set_version(version_doc)

        thumbnail_docs = version_docs
        if not thumbnail_docs:
            assets_widget = self.data["widgets"]["assets"]
            asset_docs = assets_widget.get_selected_assets()
            if len(asset_docs) > 0:
                thumbnail_docs = asset_docs

        self.data["widgets"]["thumbnail"].set_thumbnail(thumbnail_docs)

    def _set_context(self, context, refresh=True):
        """Set the selection in the interface using a context.

        The context must contain `asset` data by name.

        Note: Prior to setting context ensure `refresh` is triggered so that
              the "silos" are listed correctly, aside from that setting the
              context will force a refresh further down because it changes
              the active silo and asset.

        Args:
            context (dict): The context to apply.

        Returns:
            None

        """

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

        asset_widget = self.data["widgets"]["assets"]
        asset_widget.select_assets(asset)

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

        super(Window, self).keyPressEvent(event)
        event.setAccepted(True)  # Avoid interfering other widgets

    def show_grouping_dialog(self):
        subsets = self.data["widgets"]["subsets"]
        if not subsets.is_groupable():
            self.echo("Grouping not enabled.")
            return

        selected = []
        merged_items = []
        for item in subsets.selected_subsets(_merged=True):
            if item.get("isMerged"):
                merged_items.append(item)
            else:
                selected.append(item)

        for merged_item in merged_items:
            for child_item in merged_item.children():
                selected.append(child_item)

        if not selected:
            self.echo("No selected subset.")
            return

        dialog = SubsetGroupingDialog(
            items=selected, groups_config=self.groups_config, parent=self
        )
        dialog.grouped.connect(self._assetschanged)
        dialog.show()


class SubsetGroupingDialog(QtWidgets.QDialog):

    grouped = QtCore.Signal()

    def __init__(self, items, groups_config, parent=None):
        super(SubsetGroupingDialog, self).__init__(parent=parent)
        self.setWindowTitle("Grouping Subsets")
        self.setMinimumWidth(250)
        self.setModal(True)

        self.items = items
        self.groups_config = groups_config
        self.subsets = parent.data["widgets"]["subsets"]
        self.asset_ids = parent.data["state"]["assetIds"]

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

        active_groups = self.groups_config.active_groups(self.asset_ids)

        # Build new action group
        group = QtWidgets.QActionGroup(button)
        group_names = list()
        for data in sorted(active_groups, key=lambda x: x["order"]):
            name = data["name"]
            if name in group_names:
                continue
            group_names.append(name)
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
        self.subsets.group_subsets(name, self.asset_ids, self.items)

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
        except (AttributeError, RuntimeError):
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
        window.setStyleSheet(style.load_stylesheet())
        window.show()

        if use_context:
            context = {"asset": api.Session["AVALON_ASSET"]}
            window.set_context(context, refresh=True)
        else:
            window.refresh()

        module.window = window

        # Pull window to the front.
        module.window.raise_()
        module.window.activateWindow()


def cli(args):

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project")

    args = parser.parse_args(args)
    project = args.project

    print("Entering Project: %s" % project)

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
