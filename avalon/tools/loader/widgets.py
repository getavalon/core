import os
import sys
import datetime
import pprint
import inspect
import traceback
import collections

from ...vendor.Qt import QtWidgets, QtCore, QtGui, QtSvg
from ...vendor import qtawesome
from ... import api
from ... import pipeline
from ... import style
from ...lib import MasterVersionType

from .. import lib as tools_lib
from ..delegates import VersionDelegate, PrettyTimeDelegate
from ..widgets import OptionalMenu, OptionalAction, OptionDialog
from ..views import TreeViewSpinner

from .model import (
    SubsetsModel,
    SubsetFilterProxyModel,
    FamiliesFilterProxyModel,
)


class LoadErrorMessageBox(QtWidgets.QDialog):
    def __init__(self, messages, parent=None):
        super(LoadErrorMessageBox, self).__init__(parent)
        self.setWindowTitle("Loading failed")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body_layout = QtWidgets.QVBoxLayout(self)

        main_label = (
            "<span style='font-size:18pt;'>Failed to load items</span>"
        )
        main_label_widget = QtWidgets.QLabel(main_label, self)
        body_layout.addWidget(main_label_widget)

        item_name_template = (
            "<span style='font-weight:bold;'>Subset:</span> {}<br>"
            "<span style='font-weight:bold;'>Version:</span> {}<br>"
            "<span style='font-weight:bold;'>Representation:</span> {}<br>"
        )
        exc_msg_template = "<span style='font-weight:bold'>{}</span>"

        for exc_msg, tb, repre, subset, version in messages:
            line = self._create_line()
            body_layout.addWidget(line)

            item_name = item_name_template.format(subset, version, repre)
            item_name_widget = QtWidgets.QLabel(
                item_name.replace("\n", "<br>"), self
            )
            body_layout.addWidget(item_name_widget)

            exc_msg = exc_msg_template.format(exc_msg.replace("\n", "<br>"))
            message_label_widget = QtWidgets.QLabel(exc_msg, self)
            body_layout.addWidget(message_label_widget)

            if tb:
                tb_widget = QtWidgets.QLabel(tb.replace("\n", "<br>"), self)
                tb_widget.setTextInteractionFlags(
                    QtCore.Qt.TextBrowserInteraction
                )
                body_layout.addWidget(tb_widget)

        footer_widget = QtWidgets.QWidget(self)
        footer_layout = QtWidgets.QHBoxLayout(footer_widget)
        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        buttonBox.accepted.connect(self._on_accept)
        footer_layout.addWidget(buttonBox, alignment=QtCore.Qt.AlignRight)
        body_layout.addWidget(footer_widget)

    def _on_accept(self):
        self.close()

    def _create_line(self):
        line = QtWidgets.QFrame(self)
        line.setFixedHeight(2)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        return line


class SubsetWidget(QtWidgets.QWidget):
    """A widget that lists the published subsets for an asset"""

    active_changed = QtCore.Signal()    # active index changed
    version_changed = QtCore.Signal()   # version state changed for a subset

    default_widths = (
        ("subset", 190),
        ("asset", 130),
        ("family", 90),
        ("version", 60),
        ("time", 120),
        ("author", 85),
        ("frames", 80),
        ("duration", 60),
        ("handles", 55),
        ("step", 50)
    )

    def __init__(
        self,
        dbcon,
        groups_config,
        family_config_cache,
        enable_grouping=True,
        tool_name=None,
        parent=None
    ):
        super(SubsetWidget, self).__init__(parent=parent)

        self.dbcon = dbcon
        self.tool_name = tool_name

        model = SubsetsModel(
            dbcon,
            groups_config,
            family_config_cache,
            grouping=enable_grouping
        )
        proxy = SubsetFilterProxyModel()
        family_proxy = FamiliesFilterProxyModel(family_config_cache)
        family_proxy.setSourceModel(proxy)

        filter = QtWidgets.QLineEdit()
        filter.setPlaceholderText("Filter subsets..")

        groupable = QtWidgets.QCheckBox("Enable Grouping")
        groupable.setChecked(enable_grouping)

        top_bar_layout = QtWidgets.QHBoxLayout()
        top_bar_layout.addWidget(filter)
        top_bar_layout.addWidget(groupable)

        view = TreeViewSpinner()
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
        version_delegate = VersionDelegate(self.dbcon)
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

        for column_name, width in self.default_widths:
            idx = model.Columns.index(column_name)
            view.setColumnWidth(idx, width)

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

    def set_loading_state(self, loading, empty):
        view = self.view

        if view.is_loading != loading:
            if loading:
                view.spinner.repaintNeeded.connect(view.viewport().update)
            else:
                view.spinner.repaintNeeded.disconnect()

        view.is_loading = loading
        view.is_empty = empty

    def _repre_contexts_for_loaders_filter(self, items):
        version_docs_by_id = {
            item["version_document"]["_id"]: item["version_document"]
            for item in items
        }
        version_docs_by_subset_id = collections.defaultdict(list)
        for item in items:
            subset_id = item["version_document"]["parent"]
            version_docs_by_subset_id[subset_id].append(
                item["version_document"]
            )

        subset_docs = list(self.dbcon.find(
            {
                "_id": {"$in": list(version_docs_by_subset_id.keys())},
                "type": "subset"
            },
            {
                "schema": 1,
                "data.families": 1
            }
        ))
        subset_docs_by_id = {
            subset_doc["_id"]: subset_doc
            for subset_doc in subset_docs
        }
        version_ids = list(version_docs_by_id.keys())
        repre_docs = self.dbcon.find(
            # Query all representations for selected versions at once
            {
                "type": "representation",
                "parent": {"$in": version_ids}
            },
            # Query only name and parent from representation
            {
                "name": 1,
                "parent": 1
            }
        )
        repre_docs_by_version_id = {
            version_id: []
            for version_id in version_ids
        }
        repre_context_by_id = {}
        for repre_doc in repre_docs:
            version_id = repre_doc["parent"]
            repre_docs_by_version_id[version_id].append(repre_doc)

            version_doc = version_docs_by_id[version_id]
            repre_context_by_id[repre_doc["_id"]] = {
                "representation": repre_doc,
                "version": version_doc,
                "subset": subset_docs_by_id[version_doc["parent"]]
            }
        return repre_context_by_id, repre_docs_by_version_id

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
                for idx in range(row_index.model().rowCount(row_index)):
                    child_index = row_index.child(idx, 0)
                    item = child_index.data(self.model.ItemRole)
                    if item not in items:
                        items.append(item)

            else:
                if item not in items:
                    items.append(item)

        # Get all representation->loader combinations available for the
        # index under the cursor, so we can list the user the options.
        available_loaders = api.discover(api.Loader)
        if self.tool_name:
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
        repre_context_by_id, repre_docs_by_version_id = (
            self._repre_contexts_for_loaders_filter(items)
        )
        for item in items:
            _found_combinations = []
            version_id = item["version_document"]["_id"]
            repre_docs = repre_docs_by_version_id[version_id]
            for repre_doc in repre_docs:
                repre_context = repre_context_by_id[repre_doc["_id"]]
                for loader in pipeline.loaders_from_repre_context(
                    available_loaders,
                    repre_context
                ):
                    # skip multiple select variant if one is selected
                    if one_item_selected:
                        loaders.append((repre_doc, loader))
                        continue

                    # store loaders of first subset
                    if is_first:
                        first_loaders.append((repre_doc, loader))

                    # store combinations to compare with other subsets
                    _found_combinations.append(
                        (repre_doc["name"].lower(), loader)
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
                use_option = hasattr(loader, "options")
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
        repre_ids = []
        for item in items:
            representation = self.dbcon.find_one(
                {
                    "type": "representation",
                    "name": representation_name,
                    "parent": item["version_document"]["_id"]
                },
                {"_id": 1}
            )
            if not representation:
                self.echo("Subset '{}' has no representation '{}'".format(
                    item["subset"], representation_name
                ))
                continue
            repre_ids.append(representation["_id"])

        error_info = []
        repre_contexts = pipeline.get_repres_contexts(repre_ids, self.dbcon)
        for repre_context in repre_contexts.values():
            try:
                pipeline.load_with_repre_context(
                    loader,
                    repre_context,
                    options=options
                )

            except pipeline.IncompatibleLoaderError as exc:
                self.echo(exc)
                error_info.append((
                    "Incompatible Loader",
                    None,
                    representation["name"],
                    item["subset"],
                    item["version_document"]["name"]
                ))

            except Exception as exc:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                formatted_traceback = "".join(traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                ))
                error_info.append((
                    str(exc),
                    formatted_traceback,
                    representation["name"],
                    item["subset"],
                    item["version_document"]["name"]
                ))

        if error_info:
            box = LoadErrorMessageBox(error_info)
            box.show()

    def selected_subsets(self, _groups=False, _merged=False, _other=True):
        selection = self.view.selectionModel()
        rows = selection.selectedRows(column=0)

        subsets = list()
        if not any([_groups, _merged, _other]):
            self.echo((
                "This is a BUG: Selected_subsets args must contain"
                " at least one value set to True"
            ))
            return subsets

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
            self.dbcon.update_many(filter, update)

    def echo(self, message):
        print(message)


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

    def set_version(self, version_doc=None, version_id=None):
        # TODO expect only filling data (do not query them here!)
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

        subset = self.dbcon.find_one({
            "_id": version_doc["parent"],
            "type": "subset"
        })
        assert subset, "No valid subset parent for version"

        # Define readable creation timestamp
        created = version_doc["data"]["time"]
        created = datetime.datetime.strptime(created, "%Y%m%dT%H%M%SZ")
        created = datetime.datetime.strftime(created, "%b %d %Y %H:%M")

        comment = version_doc["data"].get("comment", None) or "No comment"

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


class ThumbnailWidget(QtWidgets.QLabel):

    aspect_ratio = (16, 9)
    max_width = 300

    def __init__(self, dbcon, parent=None):
        super(ThumbnailWidget, self).__init__(parent)
        self.dbcon = dbcon

        self.current_thumb_id = None
        self.current_thumbnail = None

        self.setAlignment(QtCore.Qt.AlignCenter)

        # TODO get res path much better way
        loader_path = os.path.dirname(os.path.abspath(__file__))
        avalon_path = os.path.dirname(os.path.dirname(loader_path))
        default_pix_path = os.path.join(
            os.path.dirname(avalon_path),
            "res", "tools", "images", "default_thumbnail.png"
        )
        self.default_pix = QtGui.QPixmap(default_pix_path)

    def height(self):
        width = self.width()
        asp_w, asp_h = self.aspect_ratio

        return (width / asp_w) * asp_h

    def width(self):
        width = super(ThumbnailWidget, self).width()
        if width > self.max_width:
            width = self.max_width
        return width

    def set_pixmap(self, pixmap=None):
        if not pixmap:
            pixmap = self.default_pix
            self.current_thumb_id = None

        self.current_thumbnail = pixmap

        pixmap = self.scale_pixmap(pixmap)
        self.setPixmap(pixmap)

    def resizeEvent(self, event):
        if not self.current_thumbnail:
            return
        cur_pix = self.scale_pixmap(self.current_thumbnail)
        self.setPixmap(cur_pix)

    def scale_pixmap(self, pixmap):
        return pixmap.scaled(
            self.width(), self.height(), QtCore.Qt.KeepAspectRatio
        )

    def set_thumbnail(self, entity=None):
        if not entity:
            self.set_pixmap()
            return

        if isinstance(entity, (list, tuple)):
            if len(entity) == 1:
                entity = entity[0]
            else:
                self.set_pixmap()
                return

        thumbnail_id = entity.get("data", {}).get("thumbnail_id")
        if thumbnail_id == self.current_thumb_id:
            if self.current_thumbnail is None:
                self.set_pixmap()
            return

        self.current_thumb_id = thumbnail_id
        if not thumbnail_id:
            self.set_pixmap()
            return

        thumbnail_ent = self.dbcon.find_one(
            {"type": "thumbnail", "_id": thumbnail_id}
        )
        if not thumbnail_ent:
            return

        thumbnail_bin = pipeline.get_thumbnail_binary(
            thumbnail_ent, "thumbnail", self.dbcon
        )
        if not thumbnail_bin:
            self.set_pixmap()
            return

        thumbnail = QtGui.QPixmap()
        thumbnail.loadFromData(thumbnail_bin)

        self.set_pixmap(thumbnail)


class VersionWidget(QtWidgets.QWidget):
    """A Widget that display information about a specific version"""
    def __init__(self, dbcon, parent=None):
        super(VersionWidget, self).__init__(parent=parent)

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Version", self)
        data = VersionTextEdit(dbcon, self)
        data.setReadOnly(True)

        layout.addWidget(label)
        layout.addWidget(data)

        self.data = data

    def set_version(self, version_doc):
        self.data.set_version(version_doc)


class FamilyListWidget(QtWidgets.QListWidget):
    """A Widget that lists all available families"""

    NameRole = QtCore.Qt.UserRole + 1
    active_changed = QtCore.Signal(list)

    def __init__(self, dbcon, family_config_cache, parent=None):
        super(FamilyListWidget, self).__init__(parent=parent)

        self.family_config_cache = family_config_cache
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

            family = self.family_config_cache.family_config(name)
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
