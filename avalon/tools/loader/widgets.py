import datetime
import pprint
import inspect

from ...vendor import Qt
from ...vendor.Qt import QtWidgets, QtCore, QtGui
from ...vendor import qtawesome
from ... import io
from ... import api
from ... import pipeline

from .. import lib as tools_lib
from ..delegates import VersionDelegate
from ..widgets import OptionalMenu, OptionalAction, OptionDialog

from .model import (
    SubsetsModel,
    SubsetFilterProxyModel,
    FamiliesFilterProxyModel,
)
from .delegates import PrettyTimeDelegate


class SubsetWidget(QtWidgets.QWidget):
    """A widget that lists the published subsets for an asset"""

    active_changed = QtCore.Signal()    # active index changed
    version_changed = QtCore.Signal()   # version state changed for a subset

    def __init__(self, enable_grouping=True, parent=None):
        super(SubsetWidget, self).__init__(parent=parent)

        model = SubsetsModel(grouping=enable_grouping)
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
        view.setStyleSheet("""
            QTreeView::item{
                padding: 5px 1px;
                border: 0px;
            }
        """)
        view.setAllColumnsShowFocus(True)

        # Set view delegates
        version_delegate = VersionDelegate()
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
                # TODO use `for` loop of index's rowCount instead of `while` loop
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
        loaders = list()

        # Bool if is selected only one subset
        one_item_selected = (len(items) == 1)

        # Prepare variables for multiple selected subsets
        first_loaders = []
        found_combinations = None

        is_first = True
        for item in items:
            _found_combinations = []

            version_id = item['version_document']['_id']
            representations = io.find({
                "type": "representation",
                "parent": version_id
            })

            for representation in representations:
                for loader in api.loaders_from_representation(
                        available_loaders,
                        representation['_id']
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

        menu = OptionalMenu(self)
        if not loaders:
            # no loaders available
            submsg = "your selection."
            if one_item_selected:
                submsg = "this version."

            msg = "No compatible loaders for {}".format(submsg)
            self.echo(msg)

            icon = qtawesome.icon(
                "fa.exclamation",
                color=QtGui.QColor(255, 51, 0)
            )

            action = OptionalAction(("*" + msg), icon, False, menu)
            menu.addAction(action)

        else:
            def sorter(value):
                """Sort the Loaders by their order and then their name"""
                Plugin = value[1]
                return Plugin.order, Plugin.__name__

            # List the available loaders
            for representation, loader in sorted(loaders, key=sorter):

                # Label
                label = getattr(loader, "label", None)
                if label is None:
                    label = loader.__name__

                # Add the representation as suffix
                label = "{0} ({1})".format(label, representation['name'])

                # Support font-awesome icons using the `.icon` and `.color`
                # attributes on plug-ins.
                icon = getattr(loader, "icon", None)
                if icon is not None:
                    try:
                        key = "fa.{0}".format(icon)
                        color = getattr(loader, "color", "white")
                        icon = qtawesome.icon(key, color=color)
                    except Exception as e:
                        print("Unable to set icon for loader "
                              "{}: {}".format(loader, e))
                        icon = None

                # Optional action
                use_option = one_item_selected and hasattr(loader, "options")
                action = OptionalAction(label, icon, use_option, menu)
                if use_option:
                    # Add option box tip
                    action.set_option_tip(loader.options)

                action.setData((representation, loader))

                # Add tooltip and statustip from Loader docstring
                tip = inspect.getdoc(loader)
                if tip:
                    action.setToolTip(tip)
                    action.setStatusTip(tip)

                menu.addAction(action)

        # Show the context action menu
        global_point = self.view.mapToGlobal(point)
        action = menu.exec_(global_point)
        if not action or not action.data():
            return

        # Find the representation name and loader to trigger
        action_representation, loader = action.data()
        representation_name = action_representation["name"]  # extension
        options = None

        # Pop option dialog
        if getattr(action, "optioned", False):
            dialog = OptionDialog(self)
            dialog.setWindowTitle(action.label + " Options")
            dialog.create(loader.options)

            if not dialog.exec_():
                return

            # Get option
            options = dialog.parse()

        # Run the loader for all selected indices, for those that have the
        # same representation available

        # Trigger
        for item in items:
            version_id = item["version_document"]["_id"]
            representation = io.find_one({
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
                api.load(Loader=loader,
                         representation=representation,
                         options=options)

            except pipeline.IncompatibleLoaderError as exc:
                self.echo(exc)
                continue

    def selected_subsets(self, _groups=False, _merged=False, _other=True):
        selection = self.view.selectionModel()
        rows = selection.selectedRows(column=0)

        subsets = list()
        if not any([_groups, _merged, _other]):
            self.echo((
                "This is a BUG: Selected_subsets args must contain"
                " at least one value set to True"
            ))
            return subset

        for row in rows:
            item = row.data(self.model.ItemRole)
            if item.get("isGroup"):
                if not _groups:
                    continue

            elif item.get("isMerged"):
                if not _merged:
                    continue
            else:
                if not _other:
                    continue

            subsets.append(item)

        return subsets

    def group_subsets(self, name, asset_ids, items):
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

        for asset_id in asset_ids:
            filter = {
                "type": "subset",
                "parent": asset_id,
                "name": {"$in": subsets},
            }
            io.update_many(filter, update)

    def echo(self, message):
        print(message)


class VersionTextEdit(QtWidgets.QTextEdit):
    """QTextEdit that displays version specific information.

    This also overrides the context menu to add actions like copying
    source path to clipboard or copying the raw data of the version
    to clipboard.

    """
    def __init__(self, parent=None):
        super(VersionTextEdit, self).__init__(parent=parent)

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

        version = io.find_one({"_id": version_id, "type": "version"})
        assert version, "Not a valid version id"

        subset = io.find_one({"_id": version["parent"], "type": "subset"})
        assert subset, "No valid subset parent for version"

        # Define readable creation timestamp
        created = version["data"]["time"]
        created = datetime.datetime.strptime(created, "%Y%m%dT%H%M%SZ")
        created = datetime.datetime.strftime(created, "%b %d %Y %H:%M")

        comment = version["data"].get("comment", None) or "No comment"

        source = version["data"].get("source", None)
        source_label = source if source else "No source"

        # Store source and raw data
        self.data["source"] = source
        self.data["raw"] = version

        data = {
            "subset": subset["name"],
            "version": version["name"],
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

        path = source.format(root=api.registered_root())
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


class FamilyListWidget(QtWidgets.QListWidget):
    """A Widget that lists all available families"""

    NameRole = QtCore.Qt.UserRole + 1
    active_changed = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(FamilyListWidget, self).__init__(parent=parent)

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

        family = io.distinct("data.family")
        families = io.distinct("data.families")
        unique_families = list(set(family + families))

        # Rebuild list
        self.blockSignals(True)
        self.clear()
        for name in sorted(unique_families):

            family = tools_lib.get_family_cached_config(name)
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
