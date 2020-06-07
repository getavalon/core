from ... import io, style
from ...vendor.Qt import Qt, QtCore, QtGui
from ...vendor import qtawesome

from ..models import TreeModel, Item
from .. import lib


def is_filtering_recursible():
    """Does Qt binding support recursive filtering for QSortFilterProxyModel?

    (NOTE) Recursive filtering was introduced in Qt 5.10.

    """
    return hasattr(QtCore.QSortFilterProxyModel,
                   "setRecursiveFilteringEnabled")


class SubsetsModel(TreeModel):

    Columns = [
        "subset",
        "family",
        "version",
        "time",
        "author",
        "frames",
        "duration",
        "handles",
        "step"
    ]

    SortAscendingRole = QtCore.Qt.UserRole + 2
    SortDescendingRole = QtCore.Qt.UserRole + 3

    def __init__(self, grouping=True, parent=None):
        super(SubsetsModel, self).__init__(parent=parent)
        self.columns_index = dict(
            (key, idx) for idx, key in enumerate(self.Columns)
        )
        self._asset_id = None
        self._grouping = grouping
        self._icons = {
            "subset": qtawesome.icon("fa.file-o", color=style.colors.default)
        }
        self._version_fetching_thread = None

    def set_asset(self, asset_id):
        self._asset_id = asset_id
        self.refresh()

    def set_grouping(self, state):
        self._grouping = state
        self.refresh()

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        # Trigger additional edit when `version` column changed
        # because it also updates the information in other columns
        if index.column() == self.columns_index["version"]:
            item = index.internalPointer()
            parent = item["_id"]
            version = io.find_one({"name": value,
                                   "type": "version",
                                   "parent": parent})
            self.set_version(index, version)

        return super(SubsetsModel, self).setData(index, value, role)

    def set_version(self, index, version):
        """Update the version data of the given index.

        Arguments:
            index (QtCore.QModelIndex): The model index.
            version (dict) Version document in the database.

        """

        assert isinstance(index, QtCore.QModelIndex)
        if not index.isValid():
            return

        item = index.internalPointer()
        assert version["parent"] == item["_id"], ("Version does not "
                                                  "belong to subset")

        # Get the data from the version
        version_data = version.get("data", dict())

        # Compute frame ranges (if data is present)
        frame_start = version_data.get(
            "frameStart",
            # backwards compatibility
            version_data.get("startFrame", None)
        )
        frame_end = version_data.get(
            "frameEnd",
            # backwards compatibility
            version_data.get("endFrame", None)
        )

        handle_start = version_data.get("handleStart", None)
        handle_end = version_data.get("handleEnd", None)
        if handle_start is not None and handle_end is not None:
            handles = "{}-{}".format(str(handle_start), str(handle_end))
        else:
            handles = version_data.get("handles", None)

        if frame_start is not None and frame_end is not None:
            # Remove superfluous zeros from numbers (3.0 -> 3) to improve
            # readability for most frame ranges
            start_clean = ("%f" % frame_start).rstrip("0").rstrip(".")
            end_clean = ("%f" % frame_end).rstrip("0").rstrip(".")
            frames = "{0}-{1}".format(start_clean, end_clean)
            duration = frame_end - frame_start + 1
        else:
            frames = None
            duration = None

        if item["schema"] != "avalon-core:subset-3.0":
            families = version_data.get("families", [None])
            family = families[0]
            family_config = lib.get_family_cached_config(family)
            item.update({
                "family": family,
                "familyLabel": family_config.get("label", family),
                "familyIcon": family_config.get("icon", None),
                "families": set(families),
            })

        item.update({
            "version": version["name"],
            "version_document": version,
            "author": version_data.get("author", None),
            "time": version_data.get("time", None),
            "frameStart": frame_start,
            "frameEnd": frame_end,
            "duration": duration,
            "handles": handles,
            "frames": frames,
            "step": version_data.get("step", None)
        })

    def clear(self):
        if self._version_fetching_thread is not None:
            self._version_fetching_thread.requestInterruption()
            while self._version_fetching_thread.isRunning():
                pass
        super(SubsetsModel, self).clear()

    def fetch_versions(self):
        """Fetch versions data for each subset in other thread
        """
        def _fetch_versions(parent=None):
            parent = parent or QtCore.QModelIndex()

            for row in range(self.rowCount(parent)):
                if lib.is_interruption_requested():
                    return

                index = self.index(row, 0, parent)
                item = index.internalPointer()
                if item.get("isGroup"):
                    _fetch_versions(parent=index)
                else:
                    # Set the version information
                    last_version = io.find_one({"type": "version",
                                                "parent": item["_id"]},
                                            sort=[("name", -1)])
                    if last_version:
                        left = index.sibling(row, 2 if "family" in item else 1)
                        right = index.sibling(row, len(self.Columns) - 1)
                        role = QtCore.Qt.EditRole
                        args = () if Qt.IsPySide or Qt.IsPyQt4 else ([role],)

                        self.set_version(index, last_version)
                        self.dataChanged.emit(left, right, *args)

        self._version_fetching_thread = lib.create_qthread(_fetch_versions)
        self._version_fetching_thread.start()

    def refresh(self):

        self.clear()
        if not self._asset_id:
            return

        self.beginResetModel()

        asset_id = self._asset_id

        active_groups = lib.get_active_group_config(asset_id)

        # Generate subset group nodes
        group_items = dict()

        if self._grouping:
            for data in active_groups:
                name = data.pop("name")
                group = Item()
                group.update({"subset": name, "isGroup": True, "childRow": 0})
                group.update(data)

                group_items[name] = group
                self.add_child(group)

        filter = {"type": "subset", "parent": asset_id}

        # Process subsets
        for subset in io.find(filter):

            data = subset.copy()
            data["subset"] = data["name"]

            group_name = subset["data"].get("subsetGroup")
            if self._grouping and group_name:
                group = group_items[group_name]
                parent = group
                group["childRow"] += 1
            else:
                parent = None

            item = Item()
            item.update(data)

            if data["schema"] == "avalon-core:subset-3.0":
                families = item["data"]["families"]
                family = families[0]
                family_config = lib.get_family_cached_config(family)
                item.update({
                    "family": family,
                    "familyLabel": family_config.get("label", family),
                    "familyIcon": family_config.get("icon", None),
                    "families": set(families),
                })

            self.add_child(item, parent=parent)

        self.endResetModel()

        lib.schedule(self.fetch_versions, 200, "versionFetching")

    def data(self, index, role):

        if not index.isValid():
            return

        if role == QtCore.Qt.DisplayRole:
            if index.column() == self.columns_index["family"]:
                # Show familyLabel instead of family
                item = index.internalPointer()
                return item.get("familyLabel", None)

            if index.column() == self.columns_index["subset"]:
                item = index.internalPointer()
                if item.get("isGroup"):
                    return "%s  (%d)" % (item["subset"], item["childRow"])
                else:
                    return item["subset"]

        if role == QtCore.Qt.DecorationRole:

            # Add icon to subset column
            if index.column() == self.columns_index["subset"]:
                item = index.internalPointer()
                if item.get("isGroup"):
                    return item["icon"]
                else:
                    return self._icons["subset"]

            # Add icon to family column
            if index.column() == self.columns_index["family"]:
                item = index.internalPointer()
                return item.get("familyIcon", None)

        if role == self.SortDescendingRole:
            item = index.internalPointer()
            if item.get("isGroup"):
                # Ensure groups be on top when sorting by descending order
                prefix = "1"
                order = item["inverseOrder"]
            else:
                prefix = "0"
                order = str(super(SubsetsModel, self).data(
                    index, QtCore.Qt.DisplayRole
                ))
            return prefix + order

        if role == self.SortAscendingRole:
            item = index.internalPointer()
            if item.get("isGroup"):
                # Ensure groups be on top when sorting by ascending order
                prefix = "0"
                order = item["order"]
            else:
                prefix = "1"
                order = str(super(SubsetsModel, self).data(
                    index, QtCore.Qt.DisplayRole
                ))
            return prefix + order

        return super(SubsetsModel, self).data(index, role)

    def flags(self, index):
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        # Make the version column editable
        if index.column() == self.columns_index["version"]:
            flags |= QtCore.Qt.ItemIsEditable

        return flags


class GroupMemberFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Provide the feature of filtering group by the acceptance of members

    The subset group nodes will not be filtered directly, the group node's
    acceptance depends on it's child subsets' acceptance.

    """

    if is_filtering_recursible():
        def _is_group_acceptable(self, index, node):
            # (NOTE) With the help of `RecursiveFiltering` feature from
            #        Qt 5.10, group always not be accepted by default.
            return False
        filter_accepts_group = _is_group_acceptable

    else:
        # Patch future function
        setRecursiveFilteringEnabled = (lambda *args: None)

        def _is_group_acceptable(self, index, model):
            # (NOTE) This is not recursive.
            for child_row in range(model.rowCount(index)):
                if self.filterAcceptsRow(child_row, index):
                    return True
            return False
        filter_accepts_group = _is_group_acceptable

    def __init__(self, *args, **kwargs):
        super(GroupMemberFilterProxyModel, self).__init__(*args, **kwargs)
        self.setRecursiveFilteringEnabled(True)


class SubsetFilterProxyModel(GroupMemberFilterProxyModel):

    def filterAcceptsRow(self, row, parent):

        model = self.sourceModel()
        index = model.index(row,
                            self.filterKeyColumn(),
                            parent)
        item = index.internalPointer()
        if item.get("isGroup"):
            return self.filter_accepts_group(index, model)
        else:
            return super(SubsetFilterProxyModel,
                         self).filterAcceptsRow(row, parent)


class FamiliesFilterProxyModel(GroupMemberFilterProxyModel):
    """Filters to specified families"""

    def __init__(self, *args, **kwargs):
        super(FamiliesFilterProxyModel, self).__init__(*args, **kwargs)
        self._families = set()

    def familyFilter(self):
        return self._families

    def setFamiliesFilter(self, values):
        """Set the families to include"""
        assert isinstance(values, (tuple, list, set))
        self._families = set(values)
        self.invalidateFilter()

    def filterAcceptsRow(self, row=0, parent=None):

        if not self._families:
            return False

        model = self.sourceModel()
        index = model.index(row, 0, parent=parent or QtCore.QModelIndex())

        # Ensure index is valid
        if not index.isValid() or index is None:
            return True

        # Get the item data and validate
        item = model.data(index, TreeModel.ItemRole)

        if item.get("isGroup"):
            return self.filter_accepts_group(index, model)

        families = item.get("families", [])

        filterable_families = set()
        for name in families:
            family_config = lib.get_family_cached_config(name)
            if not family_config.get("hideFilter"):
                filterable_families.add(name)

        if not filterable_families:
            return True

        # We want to keep the families which are not in the list
        return filterable_families.issubset(self._families)

    def sort(self, column, order):
        proxy = self.sourceModel()
        model = proxy.sourceModel()
        # We need to know the sorting direction for pinning groups on top
        if order == QtCore.Qt.AscendingOrder:
            self.setSortRole(model.SortAscendingRole)
        else:
            self.setSortRole(model.SortDescendingRole)

        super(FamiliesFilterProxyModel, self).sort(column, order)
