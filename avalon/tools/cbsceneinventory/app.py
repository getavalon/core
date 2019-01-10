import os
import sys
import logging
from functools import partial

from ...vendor.Qt import QtWidgets, QtCore
from ...vendor import qtawesome as qta
from ... import io, api, style
from .. import lib as tools_lib

# todo(roy): refactor loading from other tools
from ..projectmanager.widget import (
    preserve_expanded_rows,
    preserve_selection,
    _iter_model_rows,
)
from ..cbloader.delegates import VersionDelegate
from ..cbloader.lib import refresh_family_config

from .proxy import FilterProxyModel
from .model import InventoryModel
from .lib import switch_item

DEFAULT_COLOR = "#fb9c15"

module = sys.modules[__name__]
module.window = None


class View(QtWidgets.QTreeView):
    data_changed = QtCore.Signal()
    hierarchy_view = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(View, self).__init__(parent=parent)

        # view settings
        self.setIndentation(12)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_right_mouse_menu)
        self._hierarchy_view = False
        self._selected = None

    def enter_hierarchy(self, items):
        self._selected = set(i["objectName"] for i in items)
        self._hierarchy_view = True
        self.hierarchy_view.emit(True)
        self.data_changed.emit()
        self.expandToDepth(1)
        self.setStyleSheet("""
        QTreeView {
             border-color: #fb9c15;
        }
        """)

    def leave_hierarchy(self):
        self._hierarchy_view = False
        self.hierarchy_view.emit(False)
        self.data_changed.emit()
        self.setStyleSheet("QTreeView {}")

    def build_item_menu(self, items):
        """Create menu for the selected items"""

        menu = QtWidgets.QMenu(self)

        # update to latest version
        def _on_update_to_latest(items):
            for item in items:
                api.update(item, -1)
            self.data_changed.emit()

        update_icon = qta.icon("fa.angle-double-up", color=DEFAULT_COLOR)
        updatetolatest_action = QtWidgets.QAction(update_icon,
                                                  "Update to latest",
                                                  menu)
        updatetolatest_action.triggered.connect(
            lambda: _on_update_to_latest(items))

        # set version
        set_version_icon = qta.icon("fa.hashtag", color=DEFAULT_COLOR)
        set_version_action = QtWidgets.QAction(set_version_icon,
                                               "Set version",
                                               menu)
        set_version_action.triggered.connect(
            lambda: self.show_version_dialog(items))

        # switch asset
        switch_asset_icon = qta.icon("fa.sitemap", color=DEFAULT_COLOR)
        switch_asset_action = QtWidgets.QAction(switch_asset_icon,
                                                "Switch Asset",
                                                menu)
        switch_asset_action.triggered.connect(
            lambda: self.show_switch_dialog(items))

        # remove
        remove_icon = qta.icon("fa.remove", color=DEFAULT_COLOR)
        remove_action = QtWidgets.QAction(remove_icon, "Remove items", menu)
        remove_action.triggered.connect(
            lambda: self.show_remove_warning_dialog(items))

        # go back to flat view
        if self._hierarchy_view:
            back_to_flat_icon = qta.icon("fa.list", color=DEFAULT_COLOR)
            back_to_flat_action = QtWidgets.QAction(back_to_flat_icon,
                                                    "Back to Full-View",
                                                    menu)
            back_to_flat_action.triggered.connect(self.leave_hierarchy)

        # send items to hierarchy view
        enter_hierarchy_icon = qta.icon("fa.indent", color="#d8d8d8")
        enter_hierarchy_action = QtWidgets.QAction(enter_hierarchy_icon,
                                                   "Cherry-Pick (Hierarchy)",
                                                   menu)
        enter_hierarchy_action.triggered.connect(
            lambda: self.enter_hierarchy(items))

        # expand all items
        expandall_action = QtWidgets.QAction(menu, text="Expand all items")
        expandall_action.triggered.connect(self.expandAll)

        # collapse all items
        collapse_action = QtWidgets.QAction(menu, text="Collapse all items")
        collapse_action.triggered.connect(self.collapseAll)

        # add the actions
        has_selection = len(items)

        if has_selection:
            menu.addAction(updatetolatest_action)
            menu.addAction(set_version_action)
            menu.addAction(switch_asset_action)

            menu.addSeparator()
            menu.addAction(remove_action)

            menu.addSeparator()

        # These two actions should be able to work without selection
        menu.addAction(expandall_action)
        menu.addAction(collapse_action)

        custom_actions = self.get_custom_actions(containers=items)
        if custom_actions:
            submenu = QtWidgets.QMenu("Actions", self)
            for action in custom_actions:

                color = action.color or DEFAULT_COLOR
                icon = qta.icon("fa.%s" % action.icon, color=color)
                action_item = QtWidgets.QAction(icon, action.label, submenu)
                action_item.triggered.connect(
                    partial(self.process_custom_action, action, items))

                submenu.addAction(action_item)

            menu.addMenu(submenu)

        if has_selection:
            menu.addAction(enter_hierarchy_action)

        if self._hierarchy_view:
            menu.addAction(back_to_flat_action)

        return menu

    def get_custom_actions(self, containers):
        """Get the registered Inventory Actions

        Args:
            containers(list): collection of containers

        Returns:
            list: collection of filter and initialized actions
        """

        def sorter(Plugin):
            """Sort based on order attribute of the plugin"""
            return Plugin.order

        # Fedd an empty dict if no selection, this will ensure the compat
        # lookup always work, so plugin can interact with Scene Inventory
        # reversely.
        containers = containers or [dict()]

        # Check which action will be available in the menu
        Plugins = api.discover(api.InventoryAction)
        compatible = [p() for p in Plugins if
                      any(p.is_compatible(c) for c in containers)]

        return sorted(compatible, key=sorter)

    def process_custom_action(self, action, containers):
        """Run action and if results are returned positive update the view

        If the result is list or dict, will select view items by the result.

        Args:
            action (InventoryAction): Inventory Action instance
            containers (list): Data of currently selected items

        Returns:
            None
        """

        result = action.process(containers)
        if result:
            self.data_changed.emit()

            if isinstance(result, (list, set)):
                self.select_items_by_action(result)

            if isinstance(result, dict):
                self.select_items_by_action(result["objectNames"],
                                            result["options"])

    def select_items_by_action(self, object_names, options=None):
        """Select view items by the result of action

        Args:
            object_names (list or set): A list/set of container object name
            options (dict): GUI operation options.

        Returns:
            None

        """
        options = options or dict()

        if options.get("clear", True):
            self.clearSelection()

        object_names = set(object_names)
        if (self._hierarchy_view and
                not self._selected.issuperset(object_names)):
            # If any container not in current cherry-picked view, update
            # view before selecting them.
            self._selected.update(object_names)
            self.data_changed.emit()

        model = self.model()
        selection_model = self.selectionModel()

        select_mode = {
            "select": selection_model.Select,
            "deselect": selection_model.Deselect,
            "toggle": selection_model.Toggle,
        }[options.get("mode", "select")]

        for item in _iter_model_rows(model, 0):
            node = item.data(InventoryModel.NodeRole)
            if node.get("isGroupNode"):
                continue

            name = node.get("objectName")
            if name in object_names:
                self.scrollTo(item)  # Ensure item is visible
                selection_model.select(item, select_mode)
                object_names.remove(name)

            if len(object_names) == 0:
                break

    def show_right_mouse_menu(self, pos):
        """Display the menu when at the position of the item clicked"""

        globalpos = self.viewport().mapToGlobal(pos)

        if not self.selectionModel().hasSelection():
            print("No selection")
            # Build menu without selection, feed an empty list
            menu = self.build_item_menu([])
            menu.exec_(globalpos)
            return

        active = self.currentIndex()  # index under mouse
        active = active.sibling(active.row(), 0)  # get first column

        # move index under mouse
        indices = self.get_indices()
        if active in indices:
            indices.remove(active)

        indices.append(active)

        # Extend to the sub-items
        all_indices = self.extend_to_children(indices)
        nodes = [dict(i.data(InventoryModel.NodeRole)) for i in all_indices
                 if i.parent().isValid()]

        if self._hierarchy_view:
            # Ensure no group node
            nodes = [n for n in nodes if not n.get("isGroupNode")]

        menu = self.build_item_menu(nodes)
        menu.exec_(globalpos)

    def get_indices(self):
        """Get the selected rows"""
        selection_model = self.selectionModel()
        return selection_model.selectedRows()

    def extend_to_children(self, indices):
        """Extend the indices to the children indices.

        Top-level indices are extended to its children indices. Sub-items
        are kept as is.

        Args:
            indices (list): The indices to extend.

        Returns:
            list: The children indices

        """
        def get_children(i):
            model = i.model()
            rows = model.rowCount(parent=i)
            for row in range(rows):
                child = model.index(row, 0, parent=i)
                yield child

        subitems = set()
        for i in indices:
            valid_parent = i.parent().isValid()
            if valid_parent and i not in subitems:
                subitems.add(i)

                if self._hierarchy_view:
                    # Assume this is a group node
                    for child in get_children(i):
                        subitems.add(child)
            else:
                # is top level node
                for child in get_children(i):
                    subitems.add(child)

        return list(subitems)

    def show_version_dialog(self, items):
        """Create a dialog with the available versions for the selected file

        Args:
            items (list): list of items to run the "set_version" for

        Returns:
            None
        """

        active = items[-1]

        # Get available versions for active representation
        representation_id = io.ObjectId(active["representation"])
        representation = io.find_one({"_id": representation_id})
        version = io.find_one({"_id": representation["parent"]})

        versions = io.find({"parent": version["parent"]},
                           sort=[("name", 1)])
        versions = list(versions)

        current_version = active["version"]

        # Get index among the listed versions
        index = len(versions) - 1
        for i, version in enumerate(versions):
            if version["name"] == current_version:
                index = i
                break

        versions_by_label = dict()
        labels = []
        for version in versions:
            label = "v{0:03d}".format(version["name"])
            labels.append(label)
            versions_by_label[label] = version

        label, state = QtWidgets.QInputDialog.getItem(self,
                                                      "Set version..",
                                                      "Set version number "
                                                      "to",
                                                      labels,
                                                      current=index,
                                                      editable=False)
        if not state:
            return

        if label:
            version = versions_by_label[label]["name"]
            for item in items:
                api.update(item, version)
            # refresh model when done
            self.data_changed.emit()

    def show_switch_dialog(self, items):
        """Display Switch dialog"""
        dialog = SwitchAssetDialog(self, items)
        dialog.switched.connect(self.data_changed.emit)
        dialog.show()

    def show_remove_warning_dialog(self, items):
        """Prompt a dialog to inform the user the action will remove items"""

        accept = QtWidgets.QMessageBox.Ok
        buttons = accept | QtWidgets.QMessageBox.Cancel

        message = ("Are you sure you want to remove "
                   "{} item(s)".format(len(items)))
        state = QtWidgets.QMessageBox.question(self, "Are you sure?",
                                               message,
                                               buttons=buttons,
                                               defaultButton=accept)

        if state != accept:
            return

        for item in items:
            api.remove(item)
        self.data_changed.emit()


class SearchComboBox(QtWidgets.QComboBox):
    """Searchable ComboBox with empty placeholder value as first value"""

    def __init__(self, parent=None, placeholder=""):
        super(SearchComboBox, self).__init__(parent)

        self.setEditable(True)
        self.setInsertPolicy(self.NoInsert)
        self.lineEdit().setPlaceholderText(placeholder)

        # Apply completer settings
        completer = self.completer()
        completer.setCompletionMode(completer.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Force style sheet on popup menu
        # It won't take the parent stylesheet for some reason
        # todo: better fix for completer popup stylesheet
        if module.window:
            popup = completer.popup()
            popup.setStyleSheet(module.window.styleSheet())

    def populate(self, items):
        self.clear()
        self.addItems([""])     # ensure first item is placeholder
        self.addItems(items)

    def get_valid_value(self):
        """Return the current text if it's a valid value else None

        Note: The empty placeholder value is valid and returns as ""

        """

        text = self.currentText()
        lookup = set(self.itemText(i) for i in range(self.count()))
        if text not in lookup:
            return None

        return text


class SwitchAssetDialog(QtWidgets.QDialog):
    """Widget to support asset switching"""

    switched = QtCore.Signal()

    def __init__(self, parent=None, items=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.setModal(True)  # Force and keep focus dialog

        self.log = logging.getLogger(self.__class__.__name__)

        self._items = items

        self._assets_box = SearchComboBox(placeholder="<asset>")
        self._subsets_box = SearchComboBox(placeholder="<subset>")
        self._representations_box = SearchComboBox(
            placeholder="<representation>")

        input_layout = QtWidgets.QHBoxLayout()

        accept_icon = qta.icon("fa.check", color="white")
        accept_btn = QtWidgets.QPushButton()
        accept_btn.setIcon(accept_icon)
        accept_btn.setFixedWidth(24)
        accept_btn.setFixedHeight(24)

        input_layout.addWidget(self._assets_box)
        input_layout.addWidget(self._subsets_box)
        input_layout.addWidget(self._representations_box)
        input_layout.addWidget(accept_btn)

        self._input_layout = input_layout
        self._accept_btn = accept_btn

        self.setLayout(input_layout)
        self.setWindowTitle("Switch selected items ...")

        self.connections()

        self.refresh()

        self.setFixedSize(self.sizeHint())  # Lock window size

        # Set default focus to accept button so you don't directly type in
        # first asset field, this also allows to see the placeholder value.
        accept_btn.setFocus()

    def connections(self):
        self._accept_btn.clicked.connect(self._on_accept)

    def refresh(self):
        """Build the need comboboxes with content"""

        assets = sorted(self._get_assets())
        self._assets_box.populate(assets)

        subsets = sorted(self._get_subsets())
        self._subsets_box.populate(subsets)

        representations = sorted(self._get_representations())
        self._representations_box.populate(representations)

    def _get_assets(self):
        return self._get_document_names("asset")

    def _get_subsets(self):
        return self._get_document_names("subset")

    def _get_representations(self):
        return self._get_document_names("representation")

    def _get_document_names(self, document_type, parent=None):

        query = {"type": document_type}
        if parent:
            query["parent"] = parent["_id"]

        return io.find(query).distinct("name")

    def _on_accept(self):

        # Use None when not a valid value or when placeholder value
        asset = self._assets_box.get_valid_value() or None
        subset = self._subsets_box.get_valid_value() or None
        representation = self._representations_box.get_valid_value() or None

        if not any([asset, subset, representation]):
            self.log.error("Nothing selected")
            return

        for item in self._items:
            try:
                switch_item(item,
                            asset_name=asset,
                            subset_name=subset,
                            representation_name=representation)
            except Exception as e:
                self.log.warning(e)

        self.switched.emit()

        self.close()


class Window(QtWidgets.QDialog):
    """Scene Inventory window"""

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.resize(1100, 480)
        self.setWindowTitle(
            "Scene Inventory 1.0 - %s/%s" % (
                api.registered_root(),
                os.getenv("AVALON_PROJECT")))
        self.setObjectName("SceneInventory")
        self.setProperty("saveWindowPref", True)  # Maya only property!

        layout = QtWidgets.QVBoxLayout(self)

        # region control
        control_layout = QtWidgets.QHBoxLayout()
        filter_label = QtWidgets.QLabel("Search")
        text_filter = QtWidgets.QLineEdit()

        outdated_only = QtWidgets.QCheckBox("Filter to outdated")
        outdated_only.setToolTip("Show outdated files only")
        outdated_only.setChecked(False)

        icon = qta.icon("fa.refresh", color="white")
        refresh_button = QtWidgets.QPushButton()
        refresh_button.setIcon(icon)

        control_layout.addWidget(filter_label)
        control_layout.addWidget(text_filter)
        control_layout.addWidget(outdated_only)
        control_layout.addWidget(refresh_button)

        # endregion control

        model = InventoryModel()
        proxy = FilterProxyModel()
        view = View()
        view.setModel(proxy)

        # apply delegates
        version_delegate = VersionDelegate(self)
        column = model.COLUMNS.index("version")
        view.setItemDelegateForColumn(column, version_delegate)

        layout.addLayout(control_layout)
        layout.addWidget(view)

        self.filter = text_filter
        self.outdated_only = outdated_only
        self.view = view
        self.refresh_button = refresh_button
        self.model = model
        self.proxy = proxy

        # signals
        text_filter.textChanged.connect(self.proxy.setFilterRegExp)
        outdated_only.stateChanged.connect(self.proxy.set_filter_outdated)
        refresh_button.clicked.connect(self.refresh)
        view.data_changed.connect(self.refresh)
        view.hierarchy_view.connect(self.model.set_hierarchy_view)
        view.hierarchy_view.connect(self.proxy.set_hierarchy_view)

        # proxy settings
        proxy.setSourceModel(self.model)
        proxy.setDynamicSortFilter(True)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.data = {
            "delegates": {
                "version": version_delegate
            }
        }

        # set some nice default widths for the view
        self.view.setColumnWidth(0, 250)  # name
        self.view.setColumnWidth(1, 55)  # version
        self.view.setColumnWidth(2, 55)  # count
        self.view.setColumnWidth(3, 150)  # family
        self.view.setColumnWidth(4, 100)  # namespace

        refresh_family_config()

    def refresh(self):
        with preserve_expanded_rows(tree_view=self.view,
                                    role=self.model.UniqueRole):
            with preserve_selection(tree_view=self.view,
                                    role=self.model.UniqueRole,
                                    current_index=False):
                if self.view._hierarchy_view:
                    self.model.refresh(selected=self.view._selected)
                else:
                    self.model.refresh()


def show(root=None, debug=False, parent=None):
    """Display Scene Inventory GUI

    Arguments:
        debug (bool, optional): Run in debug-mode,
            defaults to False

    """

    try:
        module.window.close()
        del module.window
    except (RuntimeError, AttributeError):
        pass

    if debug is True:
        io.install()

        any_project = next(
            project for project in io.projects()
            if project.get("active", True) is not False
        )

        api.Session["AVALON_PROJECT"] = any_project["name"]

    with tools_lib.application():
        window = Window(parent)
        window.setStyleSheet(style.load_stylesheet())
        window.show()
        window.refresh()

        module.window = window
