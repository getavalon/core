import datetime
import pprint
import logging
import contextlib
import inspect

from ...vendor import qtawesome
from ...vendor.Qt import QtWidgets, QtCore
from ... import style, api, pipeline
from . import lib
from .. import lib as tools_lib

from .models import AssetModel, SubsetsModel
from ..models import RecursiveSortFilterProxyModel
from ..loader.model import FamiliesFilterProxyModel, SubsetFilterProxyModel

from .delegates import VersionDelegate
from ..loader.delegates import PrettyTimeDelegate

log = logging.getLogger(__name__)


class SubsetWidget(QtWidgets.QWidget):
    """A widget that lists the published subsets for an asset"""

    active_changed = QtCore.Signal()    # active index changed
    version_changed = QtCore.Signal()   # version state changed for a subset

    def __init__(self, dbcon, enable_grouping=True, parent=None):
        super(SubsetWidget, self).__init__(parent=parent)

        self.dbcon = dbcon
        self.tool_name = None
        if hasattr(parent, 'tool_name'):
            self.tool_name = parent.tool_name

        model = SubsetsModel(
            dbcon=self.dbcon, grouping=enable_grouping, parent=self
        )
        proxy = SubsetFilterProxyModel()
        family_proxy = FamiliesFilterProxyModel()
        family_proxy.setSourceModel(proxy)

        filter = QtWidgets.QLineEdit()
        filter.setPlaceholderText("Filter subsets..")

        groupable = QtWidgets.QCheckBox("Enable Grouping")
        groupable.setChecked(enable_grouping)

        top_bar_layout = QtWidgets.QHBoxLayout()
        top_bar_layout.addWidget(filter)
        top_bar_layout.addWidget(groupable)

        view = QtWidgets.QTreeView()
        view.setIndentation(20)
        view.setStyleSheet("""
            QTreeView::item{
                padding: 5px 1px;
                border: 0px;
            }
        """)
        view.setAllColumnsShowFocus(True)

        # Set view delegates
        version_delegate = VersionDelegate(dbcon=self.dbcon, parent=self)
        column = model.Columns.index("version")
        view.setItemDelegateForColumn(column, version_delegate)

        time_delegate = PrettyTimeDelegate()
        column = model.Columns.index("time")
        view.setItemDelegateForColumn(column, time_delegate)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(top_bar_layout)
        layout.addWidget(view)

        view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        view.setSortingEnabled(True)
        view.sortByColumn(1, QtCore.Qt.AscendingOrder)
        view.setAlternatingRowColors(True)

        self.data = {
            "delegates": {
                "version": version_delegate,
                "time": time_delegate
            },
            "state": {
                "groupable": groupable
            }
        }

        self.proxy = proxy
        self.model = model
        self.view = view
        self.filter = filter
        self.family_proxy = family_proxy

        # settings and connections
        self.proxy.setSourceModel(self.model)
        self.proxy.setDynamicSortFilter(True)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.view.setModel(self.family_proxy)
        self.view.customContextMenuRequested.connect(self.on_context_menu)

        header = self.view.header()
        # Enforce the columns to fit the data (purely cosmetic)
        if Qt.__binding__ in ("PySide2", "PyQt5"):
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        else:
            header.setResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        selection = view.selectionModel()
        selection.selectionChanged.connect(self.active_changed)

        version_delegate.version_changed.connect(self.version_changed)

        groupable.stateChanged.connect(self.set_grouping)

        self.filter.textChanged.connect(self.proxy.setFilterRegExp)
        self.filter.textChanged.connect(self.view.expandAll)

        self.model.refresh()

        # Expose this from the widget as a method
        self.set_family_filters = self.family_proxy.setFamiliesFilter

    def is_groupable(self):
        return self.data["state"]["groupable"].checkState()

    def set_grouping(self, state):
        with tools_lib.preserve_selection(tree_view=self.view,
                                          current_index=False):
            self.model.set_grouping(state)

    def on_context_menu(self, point):

        point_index = self.view.indexAt(point)
        if not point_index.isValid():
            return

        item = point_index.data(self.model.ItemRole)
        if item.get("isGroup"):
            return

        # Get all representation->loader combinations available for the
        # index under the cursor, so we can list the user the options.
        available_loaders = api.discover(api.Loader)
        if self.tool_name is not None:
            for loader in available_loaders:
                if hasattr(loader, 'tool_names'):
                    if not (
                        "*" in loader.tool_names or
                        self.tool_name in loader.tool_names
                    ):
                        available_loaders.remove(loader)

        loaders = list()

        version_id = item["version_document"]["_id"]
        representations = self.dbcon.find({"type": "representation",
                                   "parent": version_id})
        for representation in representations:
            for loader in lib.loaders_from_representation(
                self.dbcon,
                available_loaders,
                representation['_id']
            ):
                loaders.append((representation, loader))

        if not loaders:
            # no loaders available
            self.echo("No compatible loaders available for this version.")
            return

        def sorter(value):
            """Sort the Loaders by their order and then their name"""
            Plugin = value[1]
            return Plugin.order, Plugin.__name__

        # List the available loaders
        menu = QtWidgets.QMenu(self)
        for representation, loader in sorted(loaders, key=sorter):

            # Label
            label = getattr(loader, "label", None)
            if label is None:
                label = loader.__name__

            # Add the representation as suffix
            label = "{0} ({1})".format(label, representation["name"])

            action = QtWidgets.QAction(label, menu)
            action.setData((representation, loader))

            # Add tooltip and statustip from Loader docstring
            tip = inspect.getdoc(loader)
            if tip:
                action.setToolTip(tip)
                action.setStatusTip(tip)

            # Support font-awesome icons using the `.icon` and `.color`
            # attributes on plug-ins.
            icon = getattr(loader, "icon", None)
            if icon is not None:
                try:
                    key = "fa.{0}".format(icon)
                    color = getattr(loader, "color", "white")
                    action.setIcon(qtawesome.icon(key, color=color))
                except Exception as e:
                    print("Unable to set icon for loader "
                          "{}: {}".format(loader, e))

            menu.addAction(action)

        # Show the context action menu
        global_point = self.view.mapToGlobal(point)
        action = menu.exec_(global_point)
        if not action:
            return

        # Find the representation name and loader to trigger
        action_representation, loader = action.data()
        representation_name = action_representation["name"]  # extension

        # Run the loader for all selected indices, for those that have the
        # same representation available
        selection = self.view.selectionModel()
        rows = selection.selectedRows(column=0)

        # Ensure active point index is also used as first column so we can
        # correctly push it to the end in the rows list.
        point_index = point_index.sibling(point_index.row(), 0)

        # Ensure point index is run first.
        try:
            rows.remove(point_index)
        except ValueError:
            pass
        rows.insert(0, point_index)

        # Trigger
        for row in rows:
            item = row.data(self.model.ItemRole)
            if item.get("isGroup"):
                continue

            version_id = item["version_document"]["_id"]
            representation = self.dbcon.find_one({
                "type": "representation",
                "name": representation_name,
                "parent": version_id
            })
            if not representation:
                self.echo("Subset '{}' has no representation '{}'".format(
                          item["subset"],
                          representation_name
                          ))
                continue

            try:
                lib.load(
                    dbcon=self.dbcon,
                    Loader=loader,
                    representation=representation
                )
            except pipeline.IncompatibleLoaderError as exc:
                self.echo(exc)
                continue

    def selected_subsets(self):
        selection = self.view.selectionModel()
        rows = selection.selectedRows(column=0)

        subsets = list()
        for row in rows:
            item = row.data(self.model.ItemRole)
            if not item.get("isGroup"):
                subsets.append(item)

        return subsets

    def group_subsets(self, name, asset_id, items):
        field = "data.subsetGroup"

        if name:
            update = {"$set": {field: name}}
            self.echo("Group subsets to '%s'.." % name)
        else:
            update = {"$unset": {field: ""}}
            self.echo("Ungroup subsets..")

        subsets = list()
        for item in items:
            subsets.append(item["subset"])

        filter = {
            "type": "subset",
            "parent": asset_id,
            "name": {"$in": subsets},
        }
        self.dbcon.update_many(filter, update)

    def echo(self, message):
        print(message)


class VersionWidget(QtWidgets.QWidget):
    """A Widget that display information about a specific version"""
    def __init__(self, dbcon, parent=None):
        super(VersionWidget, self).__init__(parent=parent)
        self.dbcon = dbcon
        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Version")
        data = VersionTextEdit(dbcon=self.dbcon, parent=self)
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
    def __init__(self, dbcon, parent=None):
        super(VersionTextEdit, self).__init__(parent=parent)
        self.dbcon = dbcon
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

        version = self.dbcon.find_one(
            {"_id": version_id, "type": "version"}
        )
        assert version, "Not a valid version id"

        subset = self.dbcon.find_one(
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

        path = source.format(root=lib.registered_root(self.dbcon))
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


class FamilyListWidget(QtWidgets.QListWidget):
    """A Widget that lists all available families"""

    NameRole = QtCore.Qt.UserRole + 1
    active_changed = QtCore.Signal(list)

    def __init__(self, dbcon, parent=None):
        super(FamilyListWidget, self).__init__(parent=parent)
        self.dbcon = dbcon
        multi_select = QtWidgets.QAbstractItemView.ExtendedSelection
        self.setSelectionMode(multi_select)
        self.setAlternatingRowColors(True)
        # Enable RMB menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_right_mouse_menu)

        self.itemChanged.connect(self._on_item_changed)

    def refresh(self):
        """Refresh the listed families.

        This gets all unique families and adds them as checkable items to
        the list.

        """

        family = self.dbcon.distinct("data.family")
        families = self.dbcon.distinct("data.families")
        unique_families = list(set(family + families))

        # Rebuild list
        self.blockSignals(True)
        self.clear()
        for name in sorted(unique_families):

            family = lib.get_family_cached_config(name)
            if family.get("hideFilter"):
                continue

            label = family.get("label", name)
            icon = family.get("icon", None)

            # TODO: This should be more managable by the artist
            # Temporarily implement support for a default state in the project
            # configuration
            state = family.get("state", True)
            state = QtCore.Qt.Checked if state else QtCore.Qt.Unchecked

            item = QtWidgets.QListWidgetItem(parent=self)
            item.setText(label)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setData(self.NameRole, name)
            item.setCheckState(state)

            if icon:
                item.setIcon(icon)

            self.addItem(item)
        self.blockSignals(False)

        self.active_changed.emit(self.get_filters())

    def get_filters(self):
        """Return the checked family items"""

        items = [self.item(i) for i in
                 range(self.count())]

        return [item.data(self.NameRole) for item in items if
                item.checkState() == QtCore.Qt.Checked]

    def _on_item_changed(self):
        self.active_changed.emit(self.get_filters())

    def _set_checkstate_all(self, state):
        _state = QtCore.Qt.Checked if state is True else QtCore.Qt.Unchecked
        self.blockSignals(True)
        for i in range(self.count()):
            item = self.item(i)
            item.setCheckState(_state)
        self.blockSignals(False)
        self.active_changed.emit(self.get_filters())

    def show_right_mouse_menu(self, pos):
        """Build RMB menu under mouse at current position (within widget)"""

        # Get mouse position
        globalpos = self.viewport().mapToGlobal(pos)

        menu = QtWidgets.QMenu(self)

        # Add enable all action
        state_checked = QtWidgets.QAction(menu, text="Enable All")
        state_checked.triggered.connect(
            lambda: self._set_checkstate_all(True))
        # Add disable all action
        state_unchecked = QtWidgets.QAction(menu, text="Disable All")
        state_unchecked.triggered.connect(
            lambda: self._set_checkstate_all(False))

        menu.addAction(state_checked)
        menu.addAction(state_unchecked)

        menu.exec_(globalpos)


class AssetWidget(QtWidgets.QWidget):
    """A Widget to display a tree of assets with filter

    To list the assets of the active project:
        >>> # widget = AssetWidget()
        >>> # widget.refresh()
        >>> # widget.show()

    """

    assets_refreshed = QtCore.Signal()   # on model refresh
    selection_changed = QtCore.Signal()  # on view selection change
    current_changed = QtCore.Signal()    # on view current index change

    def __init__(self, dbcon, parent):
        super(AssetWidget, self).__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)

        self.parent_widget = parent
        self.dbcon = dbcon

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Tree View
        model = AssetModel(dbcon=self.dbcon, parent=self)
        proxy = RecursiveSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        view = AssetView()
        view.setModel(proxy)

        # Header
        header = QtWidgets.QHBoxLayout()

        icon = qtawesome.icon("fa.refresh", color=style.colors.light)
        refresh = QtWidgets.QPushButton(icon, "")
        refresh.setToolTip("Refresh items")

        filter = QtWidgets.QLineEdit()
        filter.textChanged.connect(proxy.setFilterFixedString)
        filter.setPlaceholderText("Filter assets..")

        header.addWidget(filter)
        header.addWidget(refresh)

        # Layout
        layout.addLayout(header)
        layout.addWidget(view)

        # Signals/Slots
        selection = view.selectionModel()
        selection.selectionChanged.connect(self.selection_changed)
        selection.currentChanged.connect(self.current_changed)
        # TODO this should not be set here!!!
        self.parent_widget.signal_project_changed.connect(self.refresh)

        self.refreshButton = refresh
        self.model = model
        self.proxy = proxy
        self.view = view

    def collect_data(self):
        project = self.dbcon.find_one({'type': 'project'})
        asset = self.dbcon.find_one({'_id': self.get_active_asset()})

        try:
            index = self.task_view.selectedIndexes()[0]
            task = self.task_model.itemData(index)[0]
        except Exception:
            task = None
        data = {
            'project': project['name'],
            'asset': asset['name'],
            'parents': self.get_parents(asset),
            'task': task
        }
        return data

    def get_parents(self, entity):
        output = []
        if entity.get('data', {}).get('visualParent', None) is None:
            return output
        parent = self.dbcon.find_one({'_id': entity['data']['visualParent']})
        output.append(parent['name'])
        output.extend(self.get_parents(parent))
        return output

    def _refresh_model(self):
        self.model.refresh()
        self.assets_refreshed.emit()

    def refresh(self):
        self._refresh_model()

    def get_active_asset(self):
        """Return the asset id the current asset."""
        current = self.view.currentIndex()
        return current.data(self.model.ObjectIdRole)

    def get_active_index(self):
        return self.view.currentIndex()

    def get_selected_assets(self):
        """Return the assets' ids that are selected."""
        selection = self.view.selectionModel()
        rows = selection.selectedRows()
        return [row.data(self.model.ObjectIdRole) for row in rows]

    def select_assets(self, assets, expand=True):
        """Select assets by name.

        Args:
            assets (list): List of asset names
            expand (bool): Whether to also expand to the asset in the view

        Returns:
            None

        """
        # TODO: Instead of individual selection optimize for many assets

        assert isinstance(assets,
                          (tuple, list)), "Assets must be list or tuple"

        # Clear selection
        selection_model = self.view.selectionModel()
        selection_model.clearSelection()

        # Select
        mode = selection_model.Select | selection_model.Rows
        for index in tools_lib.iter_model_rows(self.proxy,
                                      column=0,
                                      include_root=False):
            data = index.data(self.model.ItemRole)
            name = data['name']
            if name in assets:
                selection_model.select(index, mode)

                if expand:
                    self.view.expand(index)

                # Set the currently active index
                self.view.setCurrentIndex(index)
