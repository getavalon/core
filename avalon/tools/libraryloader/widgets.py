import datetime
import logging
import inspect

from ...vendor import qtawesome, Qt
from ...vendor.Qt import QtWidgets, QtCore
from ... import style, api, pipeline
from . import lib
from .. import lib as tools_lib
from ...lib import MasterVersionType

from .. import widgets as tools_widgets
from ..loader import widgets as loader_widgets

from .models import AssetModel, SubsetsModel, FamiliesFilterProxyModel
from ..models import RecursiveSortFilterProxyModel
from ..loader.model import SubsetFilterProxyModel
from .delegates import VersionDelegate
from ..delegates import PrettyTimeDelegate
from ..loader.delegates import AssetDelegate
from .. views import AssetsView

log = logging.getLogger(__name__)


class SubsetWidget(loader_widgets.SubsetWidget):
    """A widget that lists the published subsets for an asset"""

    def __init__(self, dbcon, tool_name, enable_grouping=True, parent=None):
        self.dbcon = dbcon
        self.tool_name = tool_name

        super(loader_widgets.SubsetWidget, self).__init__(parent=parent)

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
        view.setObjectName("SubsetView")
        view.setIndentation(20)
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

    def on_context_menu(self, point):
        """Shows menu with loader actions on Right-click.

        Registered actions are filtered by selection and help of
        `loaders_from_representation` from avalon api. Intersection of actions
        is shown when more subset is selected. When there are not available
        actions for selected subsets then special action is shown (works as
        info message to user): "*No compatible loaders for your selection"

        """

        point_index = self.view.indexAt(point)
        if not point_index.isValid():
            return

        # Get selected subsets without groups
        selection = self.view.selectionModel()
        rows = selection.selectedRows(column=0)

        items = []
        for row_index in rows:
            item = row_index.data(self.model.ItemRole)
            if item.get("isGroup"):
                continue

            elif item.get("isMerged"):
                # TODO use `for` loop of index's rowCount
                # - instead of `while` loop
                idx = 0
                while idx < 2000:
                    child_index = row_index.child(idx, 0)
                    if not child_index.isValid():
                        break
                    item = child_index.data(self.model.ItemRole)
                    if item not in items:
                        items.append(item)
                    idx += 1
            else:
                if item not in items:
                    items.append(item)

        # Get all representation->loader combinations available for the
        # index under the cursor, so we can list the user the options.
        available_loaders = api.discover(api.Loader)
        if self.tool_name is not None:
            for loader in available_loaders:
                if hasattr(loader, "tool_names"):
                    if not (
                        "*" in loader.tool_names or
                        self.tool_name in loader.tool_names
                    ):
                        available_loaders.remove(loader)

        loaders = list()

        # Bool if is selected only one subset
        one_item_selected = (len(items) == 1)

        # Prepare variables for multiple selected subsets
        first_loaders = []
        found_combinations = None

        is_first = True
        for item in items:
            _found_combinations = []

            version_id = item["version_document"]["_id"]
            representations = self.dbcon.find({
                "type": "representation",
                "parent": version_id
            })

            for representation in representations:
                for loader in lib.loaders_from_representation(
                    self.dbcon,
                    available_loaders,
                    representation["_id"]
                ):
                    # skip multiple select variant if one is selected
                    if one_item_selected:
                        loaders.append((representation, loader))
                        continue

                    # store loaders of first subset
                    if is_first:
                        first_loaders.append((representation, loader))

                    # store combinations to compare with other subsets
                    _found_combinations.append(
                        (representation["name"].lower(), loader)
                    )

            # skip multiple select variant if one is selected
            if one_item_selected:
                continue

            is_first = False
            # Store first combinations to compare
            if found_combinations is None:
                found_combinations = _found_combinations
            # Intersect found combinations with all previous subsets
            else:
                found_combinations = list(
                    set(found_combinations) & set(_found_combinations)
                )

        if not one_item_selected:
            # Filter loaders from first subset by intersected combinations
            for repre, loader in first_loaders:
                if (repre["name"], loader) not in found_combinations:
                    continue

                loaders.append((repre, loader))

        menu = QtWidgets.QMenu(self)
        if not loaders:
            # no loaders available
            if one_item_selected:
                self.echo("No compatible loaders available for this version.")
                return

            self.echo("No compatible loaders available for your selection.")
            action = QtWidgets.QAction(
                "*No compatible loaders for your selection", menu
            )
            menu.addAction(action)

        else:
            def sorter(value):
                """Sort the Loaders by their order and then their name."""
                Plugin = value[1]
                return Plugin.order, Plugin.__name__

            # List the available loaders
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
        if not action or not action.data():
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
        for item in items:
            version_id = item["version_document"]["_id"]
            representation = self.dbcon.find_one({
                "type": "representation",
                "name": representation_name,
                "parent": version_id
            })
            if not representation:
                self.echo("Subset '{}' has no representation '{}'".format(
                    item["subset"], representation_name
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


class VersionWidget(loader_widgets.VersionWidget):
    """A Widget that display information about a specific version."""

    def __init__(self, dbcon, parent=None):
        super(loader_widgets.VersionWidget, self).__init__(parent=parent)
        self.dbcon = dbcon
        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Version", self)
        data = VersionTextEdit(dbcon=self.dbcon, parent=self)
        data.setReadOnly(True)

        layout.addWidget(label)
        layout.addWidget(data)

        self.data = data


class VersionTextEdit(loader_widgets.VersionTextEdit):
    """QTextEdit that displays version specific information.

    This also overrides the context menu to add actions like copying
    source path to clipboard or copying the raw data of the version
    to clipboard.

    """

    def __init__(self, dbcon, parent=None):
        self.dbcon = dbcon
        super(VersionTextEdit, self).__init__(parent=parent)

    def set_version(self, version_doc=None, version_id=None):
        if not version_doc and not version_id:
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

        if not version_doc:
            version_doc = self.dbcon.find_one({
                "_id": version_id,
                "type": {"$in": ["version", "master_version"]}
            })
            assert version_doc, "Not a valid version id"

        if version_doc["type"] == "master_version":
            _version_doc = self.dbcon.find_one({
                "_id": version_doc["version_id"],
                "type": "version"
            })
            version_doc["data"] = _version_doc["data"]
            version_doc["name"] = MasterVersionType(
                _version_doc["name"]
            )

        subset = self.dbcon.find_one(
            {"_id": version_doc["parent"], "type": "subset"}
        )
        assert subset, "No valid subset parent for version"

        # Define readable creation timestamp
        created = version_doc["data"]["time"]
        created = datetime.datetime.strptime(created, "%Y%m%dT%H%M%SZ")
        created = datetime.datetime.strftime(created, "%b %d %Y %H:%M")

        comment = (version_doc["data"].get("comment") or "").strip() or (
            "No comment"
        )

        source = version_doc["data"].get("source", None)
        source_label = source if source else "No source"

        # Store source and raw data
        self.data["source"] = source
        self.data["raw"] = version_doc

        if version_doc["type"] == "master_version":
            version_name = "Master"
        else:
            version_name = tools_lib.format_version(version_doc["name"])

        data = {
            "subset": subset["name"],
            "version": version_name,
            "comment": comment,
            "created": created,
            "source": source_label
        }

        self.setHtml((
            "<h2>{subset}</h2>"
            "<h3>{version}</h3>"
            "<b>Comment</b><br>"
            "{comment}<br><br>"

            "<b>Created</b><br>"
            "{created}<br><br>"

            "<b>Source</b><br>"
            "{source}"
        ).format(**data))

    def on_copy_source(self):
        """Copy formatted source path to clipboard"""
        source = self.data.get("source", None)
        if not source:
            return

        path = source.format(root=lib.registered_root(self.dbcon))
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(path)


class FamilyListWidget(loader_widgets.FamilyListWidget):
    """A Widget that lists all available families"""

    NameRole = QtCore.Qt.UserRole + 1
    active_changed = QtCore.Signal(list)

    def __init__(self, dbcon, parent=None):
        self.dbcon = dbcon
        super(FamilyListWidget, self).__init__(parent=parent)

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


class AssetWidget(tools_widgets.AssetWidget):
    """A Widget to display a tree of assets with filter

    To list the assets of the active project:
        >>> # widget = AssetWidget()
        >>> # widget.refresh()
        >>> # widget.show()

    """

    assets_refreshed = QtCore.Signal()   # on model refresh
    selection_changed = QtCore.Signal()  # on view selection change
    current_changed = QtCore.Signal()    # on view current index change

    def __init__(self, dbcon, multiselection=False, parent=None):
        super(tools_widgets.AssetWidget, self).__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)

        self.dbcon = dbcon

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Tree View
        model = AssetModel(dbcon=self.dbcon, parent=self)
        proxy = RecursiveSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        view = AssetsView()
        view.setModel(proxy)
        if multiselection:
            asset_delegate = AssetDelegate()
            view.setSelectionMode(view.ExtendedSelection)
            view.setItemDelegate(asset_delegate)

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
        # self.parent_widget.signal_project_changed.connect(self.refresh)
        refresh.clicked.connect(self.refresh)

        self.refreshButton = refresh
        self.model = model
        self.proxy = proxy
        self.view = view
