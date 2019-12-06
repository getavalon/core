import os
import sys
import time

from .io_nonsingleton import DbConnector
from ...vendor.Qt import QtWidgets, QtCore
from ... import style
from .. import lib as tools_lib
from . import lib
from .widgets import (
    SubsetWidget,
    VersionWidget,
    FamilyListWidget,
    AssetWidget
)
from ..loader.widgets import ThumbnailWidget
from .models import AssetModel

from pypeapp import config

module = sys.modules[__name__]
module.window = None

# Custom roles
DocumentRole = AssetModel.DocumentRole


class Window(QtWidgets.QDialog):
    """Asset loader interface"""

    tool_title = "Library Loader 0.5"
    tool_name = "library_loader"

    def __init__(
        self, parent=None, icon=None, show_projects=False, show_libraries=True
    ):
        super(Window, self).__init__(parent)

        # Enable minimize and maximize for app
        self.setWindowTitle(self.tool_title)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        if icon is not None:
            self.setWindowIcon(icon)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()
        footer.setFixedHeight(20)

        container = QtWidgets.QWidget()

        self.dbcon = DbConnector()
        self.dbcon.install()
        self.dbcon.activate_project(None)

        self.show_projects = show_projects
        self.show_libraries = show_libraries

        assets = AssetWidget(
            dbcon=self.dbcon, multiselection=True, parent=self
        )
        families = FamilyListWidget(dbcon=self.dbcon, parent=self)
        subsets = SubsetWidget(
            dbcon=self.dbcon, tool_name=self.tool_name, parent=self
        )
        version = VersionWidget(dbcon=self.dbcon, parent=self)
        thumbnail = ThumbnailWidget(dbcon=self.dbcon)

        thumb_ver_body = QtWidgets.QWidget()
        thumb_ver_layout = QtWidgets.QVBoxLayout(thumb_ver_body)
        thumb_ver_layout.setContentsMargins(0, 0, 0, 0)
        thumb_ver_layout.addWidget(thumbnail)
        thumb_ver_layout.addWidget(version)

        # Project
        self.combo_projects = QtWidgets.QComboBox()

        # Create splitter to show / hide family filters
        asset_filter_splitter = QtWidgets.QSplitter()
        asset_filter_splitter.setOrientation(QtCore.Qt.Vertical)
        asset_filter_splitter.addWidget(self.combo_projects)
        asset_filter_splitter.addWidget(assets)
        asset_filter_splitter.addWidget(families)
        asset_filter_splitter.setStretchFactor(1, 65)
        asset_filter_splitter.setStretchFactor(2, 35)

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
                "template": None,
                "locations": list(),
                "context": {
                    "root": None,
                    "project": None,
                    "assets": None,
                    "assetIds": None,
                    "silo": None,
                    "subset": None,
                    "version": None,
                    "representation": None,
                },
            }
        }

        families.active_changed.connect(subsets.set_family_filters)
        assets.selection_changed.connect(self.on_assetschanged)
        assets.refreshButton.clicked.connect(self.on_refresh_clicked)
        subsets.active_changed.connect(self.on_subsetschanged)
        subsets.version_changed.connect(self.on_versionschanged)
        self.combo_projects.currentTextChanged.connect(self.on_project_change)

        # Set default thumbnail on start
        thumbnail.set_thumbnail(None)

        # Try set default project
        self._set_projects(True)

        # Defaults
        self.resize(1330, 700)

    def on_refresh_clicked(self):
        self._set_projects()

    def _set_projects(self, default=False):
        projects = self.get_filtered_projects()

        project_name = self.combo_projects.currentText()
        if default:
            project_name = self.get_default_project()

        self.combo_projects.clear()
        if len(projects) > 0:
            self.combo_projects.addItems(projects)

        project_set = False
        if project_name:
            index = self.combo_projects.findText(
                project_name, QtCore.Qt.MatchFixedString
            )
            if index:
                project_set = True
                self.combo_projects.setCurrentIndex(index)

        if not project_set:
            project_name = None

    def get_filtered_projects(self):
        projects = list()
        for project in self.dbcon.projects():
            is_library = project.get("data", {}).get("library_project", False)
            if (
                (is_library and self.show_libraries) or
                (not is_library and self.show_projects)
            ):
                projects.append(project["name"])

        return projects

    def on_project_change(self):
        projects = self.get_filtered_projects()
        project_name = self.combo_projects.currentText()
        self.dbcon.activate_project(project_name)

        _config = lib.find_config(self.dbcon)
        if hasattr(_config, "install"):
            _config.install()
        else:
            print(
                "Config `%s` has no function `install`" % _config.__name__
            )

        lib.refresh_family_config_cache(self.dbcon)
        lib.refresh_group_config_cache(self.dbcon)

        self._refresh()
        self._assetschanged()

        title = "{} - {}"
        if self.dbcon.active_project() is None:
            title = title.format(
                self.tool_title,
                "No project selected"
            )
        else:
            title = title.format(
                self.tool_title,
                os.path.sep.join([
                    lib.registered_root(self.dbcon),
                    self.dbcon.active_project()
                ])
            )
        self.setWindowTitle(title)

    def get_default_project(self):
        # looks into presets if any default library is set
        # - returns name of library from presets if exists in db
        # - if was not found or not set then returns first existing project
        # - returns `None` if any project was found in db
        name = None
        presets = config.get_presets().get("tools", {}).get(
            "library_loader", {}
        )
        if self.show_projects:
            name = presets.get("default_project")
        if self.show_libraries and not name:
            name = presets.get("default_library")

        projects = self.get_filtered_projects()

        if name and name in projects:
            return name
        elif len(projects) > 0:
            return projects[0]
        return None

    @property
    def current_project(self):
        if (
            not self.dbcon.active_project() or
            self.dbcon.active_project() == ""
        ):
            return None

        return self.dbcon.active_project()

    # -------------------------------
    # Delay calling blocking methods
    # -------------------------------

    def refresh(self):
        self.echo("Fetching results..")
        tools_lib.schedule(self._refresh, 50, channel="mongo")

    def on_assetschanged(self, *args):
        self.echo("Fetching asset..")
        tools_lib.schedule(self._assetschanged, 50, channel="mongo")

    def on_subsetschanged(self, *args):
        self.echo("Fetching subset..")
        tools_lib.schedule(self._subsetschanged, 50, channel="mongo")

    def on_versionschanged(self, *args):
        self.echo("Fetching version..")
        tools_lib.schedule(self._versionschanged, 150, channel="mongo")

    def set_context(self, context, refresh=True):
        self.echo("Setting context: {}".format(context))
        lib.schedule(
            lambda: self._set_context(context, refresh=refresh),
            50, channel="mongo"
        )

    # ------------------------------

    def _refresh(self):
        """Load assets from database"""
        if self.current_project is None:
            return
        # Ensure a project is loaded
        project = self.dbcon.find_one({"type": "project"})
        assert project, "This is a bug"

        assets_widget = self.data["widgets"]["assets"]
        assets_widget.refresh()
        assets_widget.setFocus()

        families = self.data["widgets"]["families"]
        families.refresh()

        # Update state
        state = self.data["state"]
        state["template"] = project["config"]["template"]["publish"]
        state["context"]["root"] = lib.registered_root(self.dbcon)
        state["context"]["project"] = project["name"]

    def clear_assets_underlines(self):
        last_asset_ids = self.data["state"]["context"]["assetIds"]
        if not last_asset_ids:
            return

        assets_widget = self.data["widgets"]["assets"]
        id_role = assets_widget.model.ObjectIdRole

        for index in tools_lib.iter_model_rows(assets_widget.model, 0):
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

        subsets_widget.model.clear()
        self.clear_assets_underlines()

        # filter None docs they are silo
        asset_docs = assets_widget.get_selected_assets()
        if len(asset_docs) == 0:
            return

        asset_ids = [a["_id"] for a in asset_docs]
        asset_names = [a["name"] for a in asset_docs]
        subsets_widget.model.set_assets(asset_ids)
        subsets_widget.view.setColumnHidden(
            subsets_widget.model.Columns.index("asset"),
            len(asset_ids) < 2
        )

        # Clear the version information on asset change
        self.data["widgets"]["version"].set_version(None)
        self.data["widgets"]["thumbnail"].set_thumbnail(asset_docs)

        self.data["state"]["context"]["assets"] = asset_names
        self.data["state"]["context"]["assetIds"] = asset_ids
        silo = None
        if len(asset_docs) == 1:
            silo = asset_docs[0].get("silo")
        self.data["state"]["context"]["silo"] = silo

        self.echo("Duration: %.3fs" % (time.time() - t1))

    def _subsetschanged(self):
        asset_ids = self.data["state"]["context"]["assetIds"]
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
        version_id = None
        active = selection.currentIndex()
        rows = selection.selectedRows(column=active.column())
        if active and active in rows:
            item = active.data(subsets.model.ItemRole)
            if (
                item is not None and
                not (item.get("isGroup") or item.get("isMerged"))
            ):
                version_id = item["version_document"]["_id"]

        if rows:
            version_docs = []
            for index in rows:
                if not index or not index.isValid():
                    continue
                item = index.data(subsets.model.ItemRole)
                if (
                    item is None or
                    item.get("isGroup") or
                    item.get("isMerged")
                ):
                    continue
                version_docs.append(item["version_document"])

        self.data["widgets"]["version"].set_version(version_id)
        self.data["widgets"]["thumbnail"].set_thumbnail(version_docs)

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

        tools_lib.schedule(widget.hide, 5000, channel="message")

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

        # self.dbcon.uninstall()

        print("Good bye")
        return super(Window, self).closeEvent(event)


def show(
    debug=False, parent=None, icon=None,
    show_projects=False, show_libraries=True
):
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

    with tools_lib.application():
        window = Window(parent, icon, show_projects, show_libraries)
        window.setStyleSheet(style.load_stylesheet())
        window.show()

        module.window = window


def cli(args):

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project")

    show(show_projects=True, show_libraries=True)
