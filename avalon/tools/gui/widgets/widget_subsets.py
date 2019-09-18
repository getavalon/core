import inspect

from ....vendor import qtawesome, Qt
from ....vendor.Qt import QtCore, QtWidgets

from .... import pipeline, api, io

from ..delegates import PrettyTimeDelegate, VersionDelegate
from ..models import (
    SubsetModel, SubsetFilterProxyModel, FamilyFilterProxyModel
)

from .lib import preserve_selection


class SubsetsWidget(QtWidgets.QWidget):
    """A widget that lists the published subsets for an asset"""

    active_changed = QtCore.Signal()    # active index changed
    version_changed = QtCore.Signal()   # version state changed for a subset

    def __init__(self, enable_grouping=True, parent=None):
        super(SubsetsWidget, self).__init__(parent=parent)

        model = SubsetModel(grouping=enable_grouping)
        proxy = SubsetFilterProxyModel()
        family_proxy = FamilyFilterProxyModel()
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
        version_delegate = VersionDelegate()
        column = model.COLUMNS.index("version")
        view.setItemDelegateForColumn(column, version_delegate)

        time_delegate = PrettyTimeDelegate()
        column = model.COLUMNS.index("time")
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
        with preserve_selection(tree_view=self.view,
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
        loaders = list()

        version_id = item['version_document']['_id']
        representations = io.find({"type": "representation",
                                   "parent": version_id})
        for representation in representations:
            for loader in api.loaders_from_representation(
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
            label = "{0} ({1})".format(label, representation['name'])

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
        representation_name = action_representation['name']  # extension

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
            representation = io.find_one({"type": "representation",
                                          "name": representation_name,
                                          "parent": version_id})
            if not representation:
                self.echo("Subset '{}' has no representation '{}'".format(
                          item["subset"],
                          representation_name
                          ))
                continue

            try:
                api.load(Loader=loader, representation=representation)
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
        io.update_many(filter, update)

    def echo(self, message):
        print(message)
