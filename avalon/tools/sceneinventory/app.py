import os
import sys
import logging
from functools import partial

from ...vendor.Qt import QtWidgets, QtCore
from ...vendor import qtawesome
from ... import io, api, style

from .. import lib as tools_lib
from ..delegates import VersionDelegate

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

        update_icon = qtawesome.icon("fa.angle-double-up", color=DEFAULT_COLOR)
        updatetolatest_action = QtWidgets.QAction(update_icon,
                                                  "Update to latest",
                                                  menu)
        updatetolatest_action.triggered.connect(
            lambda: _on_update_to_latest(items))

        # set version
        set_version_icon = qtawesome.icon("fa.hashtag", color=DEFAULT_COLOR)
        set_version_action = QtWidgets.QAction(set_version_icon,
                                               "Set version",
                                               menu)
        set_version_action.triggered.connect(
            lambda: self.show_version_dialog(items))

        # switch asset
        switch_asset_icon = qtawesome.icon("fa.sitemap", color=DEFAULT_COLOR)
        switch_asset_action = QtWidgets.QAction(switch_asset_icon,
                                                "Switch Asset",
                                                menu)
        switch_asset_action.triggered.connect(
            lambda: self.show_switch_dialog(items))

        # remove
        remove_icon = qtawesome.icon("fa.remove", color=DEFAULT_COLOR)
        remove_action = QtWidgets.QAction(remove_icon, "Remove items", menu)
        remove_action.triggered.connect(
            lambda: self.show_remove_warning_dialog(items))

        # go back to flat view
        if self._hierarchy_view:
            back_to_flat_icon = qtawesome.icon("fa.list", color=DEFAULT_COLOR)
            back_to_flat_action = QtWidgets.QAction(back_to_flat_icon,
                                                    "Back to Full-View",
                                                    menu)
            back_to_flat_action.triggered.connect(self.leave_hierarchy)

        # send items to hierarchy view
        enter_hierarchy_icon = qtawesome.icon("fa.indent", color="#d8d8d8")
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
                icon = qtawesome.icon("fa.%s" % action.icon, color=color)
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

        for item in tools_lib.iter_model_rows(model, 0):
            node = item.data(InventoryModel.ItemRole)
            if node.get("isGroupNode"):
                continue

            name = node.get("objectName")
            if name in object_names:
                self.scrollTo(item)  # Ensure item is visible
                flags = select_mode | selection_model.Rows
                selection_model.select(item, flags)

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
        nodes = [dict(i.data(InventoryModel.ItemRole)) for i in all_indices
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

    _fill_check = False
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

        self._asset_label = QtWidgets.QLabel("")
        self._subset_label = QtWidgets.QLabel("")
        self._repre_label = QtWidgets.QLabel("")

        main_layout = QtWidgets.QVBoxLayout()
        context_layout = QtWidgets.QHBoxLayout()
        asset_layout = QtWidgets.QVBoxLayout()
        subset_layout = QtWidgets.QVBoxLayout()
        repre_layout = QtWidgets.QVBoxLayout()

        accept_icon = qtawesome.icon("fa.check", color="white")
        accept_btn = QtWidgets.QPushButton()
        accept_btn.setIcon(accept_icon)
        accept_btn.setFixedWidth(24)
        accept_btn.setFixedHeight(24)

        asset_layout.addWidget(self._assets_box)
        asset_layout.addWidget(self._asset_label)
        subset_layout.addWidget(self._subsets_box)
        subset_layout.addWidget(self._subset_label)
        repre_layout.addWidget(self._representations_box)
        repre_layout.addWidget(self._repre_label)

        context_layout.addLayout(asset_layout)
        context_layout.addLayout(subset_layout)
        context_layout.addLayout(repre_layout)
        context_layout.addWidget(accept_btn)

        self._accept_btn = accept_btn

        self._assets_box.currentIndexChanged.connect(self.refresh)
        self._subsets_box.currentIndexChanged.connect(self.refresh)
        self._representations_box.currentIndexChanged.connect(self.refresh)
        self._accept_btn.clicked.connect(self._on_accept)

        main_layout.addLayout(context_layout)
        self.setLayout(main_layout)
        self.setWindowTitle("Switch selected items ...")

        self._prepare_content_data()
        self.refresh(True)

        self.setFixedSize(self.sizeHint())  # Lock window size

        # Set default focus to accept button so you don't directly type in
        # first asset field, this also allows to see the placeholder value.
        accept_btn.setFocus()

    def _prepare_content_data(self):
        repre_ids = [
            io.ObjectId(item["representation"])
            for item in self._items
        ]
        repres = list(io.find({
            "type": "representation",
            "_id": {"$in": repre_ids}
        }))
        repres_by_id = {
            repre["_id"]: repre
            for repre in repres
        }

        content_repres = {}
        missing_repres = []
        for repre_id in repre_ids:
            if repre_id not in repres_by_id:
                missing_repres.append(repre_id)
            else:
                content_repres[repre_id] = repres_by_id[repre_id]

        version_ids = set(
            repre["parent"]
            for repre in content_repres.values()
        )
        version_docs = io.find({
            "type": "version",
            "_id": {"$in": list(version_ids)}
        })
        content_versions = {
            version_doc["_id"]: version_doc
            for version_doc in version_docs
        }
        missing_versions = [
            version_id
            for version_id in version_ids
            if version_id not in content_versions
        ]

        subset_ids = set(
            version_doc["parent"]
            for version_doc in content_versions.values()
        )
        subset_docs = io.find({
            "type": "subset",
            "_id": {"$in": list(subset_ids)}
        })
        subsets_by_id = {
            subset_doc["_id"]: subset_doc
            for subset_doc in subset_docs
        }

        missing_subsets = []
        content_subsets = {}
        for subset_id in subset_ids:
            if subset_id not in subsets_by_id:
                missing_subsets.append(subset_id)
            else:
                content_subsets[subset_id] = subsets_by_id[subset_id]

        asset_ids = set(
            subset_doc["parent"]
            for subset_doc in content_subsets.values()
        )

        asset_docs = io.find({
            "type": "asset",
            "_id": {"$in": list(asset_ids)}
        })
        assets_by_id = {
            asset_doc["_id"]: asset_doc
            for asset_doc in asset_docs
        }

        missing_assets = []
        content_assets = {}
        for asset_id in asset_ids:
            if asset_id not in assets_by_id:
                missing_assets.append(asset_id)
            else:
                content_assets[asset_id] = assets_by_id[asset_id]

        self.content_assets = content_assets
        self.content_subsets = content_subsets
        self.content_versions = content_versions
        self.content_repres = content_repres

        self.missing_docs = (
            bool(missing_assets)
            or bool(missing_versions)
            or bool(missing_subsets)
            or bool(missing_repres)
        )

    def refresh(self, init_refresh=False):
        """Build the need comboboxes with content"""
        if not self._fill_check and not init_refresh:
            return

        self._fill_check = False

        if refresh_type < 1:
            assets = sorted(self._get_assets())
            self._assets_box.populate(assets)

        if refresh_type < 2:
            last_subset = self._subsets_box.currentText()

            subsets = sorted(self._get_subsets())
            self._subsets_box.populate(subsets)

            if (last_subset != "" and last_subset in list(subsets)):
                index = None
                for i in range(self._subsets_box.count()):
                    if last_subset == str(self._subsets_box.itemText(i)):
                        index = i
                        break
                if index is not None:
                    self._subsets_box.setCurrentIndex(index)

        if refresh_type < 3:
            last_repre = self._representations_box.currentText()

            representations = sorted(self._get_representations())
            self._representations_box.populate(representations)

            if (last_repre != "" and last_repre in list(representations)):
                index = None
                for i in range(self._representations_box.count()):
                    if last_repre == self._representations_box.itemText(i):
                        index = i
                        break
                if index is not None:
                    self._representations_box.setCurrentIndex(index)
        self._fill_check = True

        self.set_labels()
        self.validate()

    def set_labels(self):
        asset_label = self._assets_box.get_valid_value()
        subset_label = self._subsets_box.get_valid_value()
        repre_label = self._representations_box.get_valid_value()

        default = "*No changes"
        self._asset_label.setText(asset_label or default)
        self._subset_label.setText(subset_label or default)
        self._repre_label.setText(repre_label or default)

    def _get_assets(self):
        filtered_assets = []
        for asset in io.find({"type": "asset"}):
            subsets = io.find({
                "type": "subset",
                "parent": asset["_id"]
            })
            for subs in subsets:
                filtered_assets.append(asset["name"])
                break

        return filtered_assets

    def _get_subsets(self):
        # Filter subsets by asset in dropdown
        if self._assets_box.currentText() != "":
            parents = list()
            parents.append(io.find_one({
                "type": "asset",
                "name": self._assets_box.currentText()
            }))

            return self._get_document_names("subset", parents)
        # If any asset in dropdown is selected
        # - filter subsets by selected assets in scene inventory
        assets = []
        for item in self._items:
            _id = io.ObjectId(item["representation"])
            representation = io.find_one(
                {"type": "representation", "_id": _id}
            )
            version, subset, asset, project = io.parenthood(representation)
            assets.append(asset)

        possible_subsets = None
        for asset in assets:
            subsets = io.find({
                "type": "subset",
                "parent": asset["_id"]
            })
            asset_subsets = set()
            for subset in subsets:
                asset_subsets.add(subset["name"])

            if possible_subsets is None:
                possible_subsets = asset_subsets
            else:
                possible_subsets = (possible_subsets & asset_subsets)

        return list(possible_subsets)

    def _get_representations(self):
        if self._subsets_box.currentText() != "":
            subsets = []
            parents = []
            subsets.append(self._subsets_box.currentText())

            for subset in subsets:
                entity = io.find_one({
                    "type": "subset",
                    "name": subset
                })

                entity = io.find_one(
                    {
                        "type": "version",
                        "parent": entity["_id"]
                    },
                    sort=[("name", -1)]
                )
                if entity not in parents:
                    parents.append(entity)

            return self._get_document_names("representation", parents)

        versions = []
        for item in self._items:
            _id = io.ObjectId(item["representation"])
            representation = io.find_one(
                {"type": "representation", "_id": _id}
            )
            version, subset, asset, project = io.parenthood(representation)
            versions.append(version)

        possible_repres = None
        for version in versions:
            representations = io.find({
                "type": "representation",
                "parent": version["_id"]
            })
            repres = set()
            for repre in representations:
                repres.add(repre["name"])

            if possible_repres is None:
                possible_repres = repres
            else:
                possible_repres = (possible_repres & repres)

        return list(possible_repres)

    def _get_document_names(self, document_type, parents=[]):

        query = {"type": document_type}

        if len(parents) == 1:
            query["parent"] = parents[0]["_id"]
        elif len(parents) > 1:
            or_exprs = []
            for parent in parents:
                expr = {"parent": parent["_id"]}
                or_exprs.append(expr)

            query["$or"] = or_exprs

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

    def _get_asset_box_values(self):
        assets_by_id = {
            asset_doc["_id"]: asset_doc
            for asset_doc in io.find({"type": "asset"})
        }
        subsets = io.find({
            "type": "subset",
            "parent": {"$in": list(assets_by_id.keys())}
        })

        filtered_assets = []
        for subset in subsets:
            asset_name = assets_by_id[subset["parent"]]["name"]
            if asset_name not in filtered_assets:
                filtered_assets.append(asset_name)
        return sorted(filtered_assets)

    def _get_subset_box_values(self):
        selected_asset = self._assets_box.get_valid_value()
        if selected_asset:
            asset_doc = io.find_one({"type": "asset", "name": selected_asset})
            asset_ids = [asset_doc["_id"]]
        else:
            asset_ids = list(self.content_assets.keys())

        subsets = io.find({
            "type": "subset",
            "parent": {"$in": asset_ids}
        })

        subset_names_by_parent_id = collections.defaultdict(set)
        for subset in subsets:
            subset_names_by_parent_id[subset["parent"]].add(subset["name"])

        possible_subsets = None
        for subset_names in subset_names_by_parent_id.values():
            if possible_subsets is None:
                possible_subsets = subset_names
            else:
                possible_subsets = (possible_subsets & subset_names)

            if not possible_subsets:
                break

        return list(possible_subsets or list())

    def _representations_box_values(self):
        # NOTE master versions are not used because it is expected that
        # master version has same representations as latests
        selected_asset = self._assets_box.currentText()
        selected_subset = self._subsets_box.currentText()

        # If nothing is selected
        if not selected_asset and not selected_subset:
            # Find all representations of selection's subsets
            possible_repres = list(io.find({
                "type": "representation",
                "parent": {"$in": list(self.content_versions.keys())}
            }))

            possible_repres_by_parent = collections.defaultdict(set)
            for repre in possible_repres:
                possible_repres_by_parent[repre["parent"]].add(repre["name"])

            output_repres = None
            for repre_names in possible_repres_by_parent.values():
                if output_repres is None:
                    output_repres = repre_names
                else:
                    output_repres = (output_repres & repre_names)

                if not output_repres:
                    break

            return list(output_repres or list())

        if selected_asset:
            # If asset only is selected
            asset = io.find_one({"type": "asset", "name": selected_asset})
            asset_ids = [asset["_id"]]
        else:
            # If only subset is selected
            asset_ids = list(self.content_assets.keys())

        subset_query = {
            "type": "subset",
            "parent": {"$in": asset_ids}
        }
        if selected_subset:
            subset_query["name"] = selected_subset

        subsets = list(io.find(subset_query))
        if not subsets:
            return list()

        # versions
        versions = list(io.find({
            "type": "version",
            "parent": {"$in": [subset["_id"] for subset in subsets]}
        }, sort=[("name", -1)]))
        if not versions:
            return list()

        higher_versions_map = {}
        for version in versions:
            parent_id = version["parent"]
            if parent_id not in higher_versions_map:
                higher_versions_map[parent_id] = version

        higher_versions_ids = [
            version["_id"] for version in higher_versions_map.values()
        ]

        higher_version_repres = io.find({
            "type": "representation",
            "parent": {"$in": higher_versions_ids}
        })

        repre_per_version = collections.defaultdict(set)
        for repre in higher_version_repres:
            repre_per_version[repre["parent"]].add(repre["name"])

        # representations
        output_repres = None
        for repre_names in repre_per_version.values():
            if output_repres is None:
                output_repres = repre_names
            else:
                output_repres = (output_repres & repre_names)

            if not output_repres:
                break

        return list(output_repres or list())

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

        icon = qtawesome.icon("fa.refresh", color="white")
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
        column = model.Columns.index("version")
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

        tools_lib.refresh_family_config_cache()

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands
        whilst trying to name an instance.

        """

    def refresh(self):
        with tools_lib.preserve_expanded_rows(tree_view=self.view,
                                              role=self.model.UniqueRole):
            with tools_lib.preserve_selection(tree_view=self.view,
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
        parent (QtCore.QObject, optional): When provided parent the interface
            to this QObject.

    """

    try:
        module.window.close()
        del module.window
    except (RuntimeError, AttributeError):
        pass

    if debug:
        import traceback
        sys.excepthook = lambda typ, val, tb: traceback.print_last()

    with tools_lib.application():
        window = Window(parent)
        window.show()
        window.setStyleSheet(style.load_stylesheet())
        window.refresh()

        module.window = window

        # Pull window to the front.
        module.window.raise_()
        module.window.activateWindow()
