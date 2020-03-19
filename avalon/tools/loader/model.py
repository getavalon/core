from ... import io, style
from ...vendor.Qt import QtCore
from ...vendor import qtawesome

from ..models import TreeModel, Item
from .. import lib
from ...lib import MasterVersionType


def is_filtering_recursible():
    """Does Qt binding support recursive filtering for QSortFilterProxyModel?

    (NOTE) Recursive filtering was introduced in Qt 5.10.

    """
    return hasattr(QtCore.QSortFilterProxyModel,
                   "setRecursiveFilteringEnabled")


class SubsetsModel(TreeModel):
    Columns = [
        "subset",
        "asset",
        "family",
        "version",
        "time",
        "author",
        "frames",
        "duration",
        "handles",
        "step"
    ]

    column_labels_mapping = {
        "subset": "Subset",
        "asset": "Asset",
        "family": "Family",
        "version": "Version",
        "time": "Time",
        "author": "Author",
        "frames": "Frames",
        "duration": "Duration",
        "handles": "Handles",
        "step": "Step"
    }

    SortAscendingRole = QtCore.Qt.UserRole + 2
    SortDescendingRole = QtCore.Qt.UserRole + 3
    merged_subset_colors = [
        (55, 161, 222), # Light Blue
        (231, 176, 0), # Yellow
        (154, 13, 255), # Purple
        (130, 184, 30), # Light Green
        (211, 79, 63), # Light Red
        (179, 181, 182), # Grey
        (194, 57, 179), # Pink
        (0, 120, 215), # Dark Blue
        (0, 204, 106), # Dark Green
        (247, 99, 12), # Orange
    ]

    def __init__(self, grouping=True, parent=None):
        super(SubsetsModel, self).__init__(parent=parent)
        self._asset_ids = None
        self._sorter = None
        self._grouping = grouping
        self._icons = {
            "subset": qtawesome.icon("fa.file-o", color=style.colors.default)
        }

    def set_assets(self, asset_ids):
        self._asset_ids = asset_ids
        self.refresh()

    def set_grouping(self, state):
        self._grouping = state
        self.refresh()

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        # Trigger additional edit when `version` column changed
        # because it also updates the information in other columns
        if index.column() == self.Columns.index("version"):
            item = index.internalPointer()
            parent = item["_id"]
            if isinstance(value, MasterVersionType):
                versions = list(io.find({
                    "type": {"$in": ["version", "master_version"]},
                    "parent": parent
                }, sort=[("name", -1)]))

                version = None
                last_version = None
                for __version in versions:
                    if __version["type"] == "master_version":
                        version = __version
                    elif last_version is None:
                        last_version = __version

                    if version is not None and last_version is not None:
                        break

                _version = None
                for __version in versions:
                    if __version["_id"] == version["version_id"]:
                        _version = __version
                        break

                version["data"] = _version["data"]
                version["name"] = _version["name"]
                version["is_from_latest"] = (
                    last_version["_id"] == _version["_id"]
                )

            else:
                version = io.find_one({
                    "name": value,
                    "type": "version",
                    "parent": parent
                })
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

        if item["schema"] == "avalon-core:subset-3.0":
            families = item["data"]["families"]
        else:
            families = version_data.get("families", [None])

        family = families[0]
        family_config = lib.get_family_cached_config(family)

        item.update({
            "version": version["name"],
            "version_document": version,
            "author": version_data.get("author", None),
            "time": version_data.get("time", None),
            "family": family,
            "familyLabel": family_config.get("label", family),
            "familyIcon": family_config.get("icon", None),
            "families": set(families),
            "frameStart": frame_start,
            "frameEnd": frame_end,
            "duration": duration,
            "handles": handles,
            "frames": frames,
            "step": version_data.get("step", None)
        })

    def refresh(self):

        self.clear()
        self.beginResetModel()
        if not self._asset_ids:
            self.endResetModel()
            return

        active_groups = []
        for asset_id in self._asset_ids:
            result = lib.get_active_group_config(asset_id)
            if result:
                active_groups.extend(result)

        parent_filter = [{"parent": asset_id} for asset_id in self._asset_ids]
        filtered_subsets = [
            s for s in io.find({"type": "subset", "$or": parent_filter})
        ]

        asset_entities = {}
        for asset_id in self._asset_ids:
            asset_ent = io.find_one({"_id": asset_id})
            asset_entities[asset_id] = asset_ent

        # Collect last versions
        last_versions = {}
        for subset in filtered_subsets:
            last_version = io.find_one({
                "type": "version",
                "parent": subset["_id"]
            }, sort=[("name", -1)])

            master_version = io.find_one({
                "type": "master_version",
                "parent": subset["_id"]
            })
            if master_version:
                _version = io.find_one({
                    "_id": master_version["version_id"]
                })
                master_version["data"] = _version["data"]
                master_version["name"] = MasterVersionType(
                    _version["name"]
                )
                # Add information if master version is from latest version
                is_from_latest = True
                if last_version:
                    is_from_latest = last_version["_id"] == _version["_id"]
                master_version["is_from_latest"] = is_from_latest

                last_versions[subset["_id"]] = master_version
                continue

            # No published version for the subset
            last_versions[subset["_id"]] = last_version

        # Prepare data if is selected more than one asset
        process_only_single_asset = True
        merge_subsets = False
        if len(parent_filter) >= 2:
            process_only_single_asset = False
            all_subset_names = []
            multiple_asset_names = []

            for subset in filtered_subsets:
                # No published version for the subset
                if not last_versions[subset["_id"]]:
                    continue

                name = subset["name"]
                if name in all_subset_names:
                    # process_only_single_asset = False
                    merge_subsets = True
                    if name not in multiple_asset_names:
                        multiple_asset_names.append(name)
                else:
                    all_subset_names.append(name)

        # Process subsets
        row = 0
        group_items = dict()

        # When only one asset is selected
        if process_only_single_asset:
            if self._grouping:
                # Generate subset group items
                group_names = []
                for data in active_groups:
                    name = data.pop("name")
                    if name in group_names:
                        continue
                    group_names.append(name)

                    group = Item()
                    group.update({
                        "subset": name,
                        "isGroup": True,
                        "childRow": 0
                    })
                    group.update(data)

                    group_items[name] = group
                    self.add_child(group)

            row = len(group_items)
            single_asset_subsets = filtered_subsets

        # When multiple assets are selected
        else:
            single_asset_subsets = []
            multi_asset_subsets = {}

            for subset in filtered_subsets:
                last_version = last_versions[subset["_id"]]
                if not last_version:
                    continue

                data = subset.copy()
                name = data["name"]
                asset_name = asset_entities[data["parent"]]["name"]

                data["subset"] = name
                data["asset"] = asset_name

                asset_subset_data = {
                    "data": data,
                    "last_version": last_version
                }

                if name in multiple_asset_names:
                    if name not in multi_asset_subsets:
                        multi_asset_subsets[name] = {}
                    multi_asset_subsets[name][data["parent"]] = (
                        asset_subset_data
                    )
                else:
                    single_asset_subsets.append(data)

            color_count = len(self.merged_subset_colors)
            merged_names = {}
            subset_counter = 0
            total = len(multi_asset_subsets)
            str_order_temp = "%0{}d".format(len(str(total)))

            for subset_name, per_asset_data in multi_asset_subsets.items():
                subset_color = self.merged_subset_colors[
                    subset_counter % color_count
                ]
                inverse_order = total - subset_counter

                merge_group = Item()
                merge_group.update({
                    "subset": "{} ({})".format(
                        subset_name, str(len(per_asset_data))
                    ),
                    "isMerged": True,
                    "childRow": 0,
                    "subsetColor": subset_color,
                    "assetIds": [id for id in per_asset_data],

                    "icon": qtawesome.icon(
                        "fa.circle",
                        color="#{0:02x}{1:02x}{2:02x}".format(*subset_color)
                    ),
                    "order": "0{}".format(subset_name),
                    "inverseOrder": str_order_temp % inverse_order
                })

                subset_counter += 1
                row += 1
                group_items[subset_name] = merge_group
                self.add_child(merge_group)

                merge_group_index = self.createIndex(0, 0, merge_group)

                for asset_id, asset_subset_data in per_asset_data.items():
                    last_version = asset_subset_data["last_version"]
                    data = asset_subset_data["data"]

                    row_ = merge_group["childRow"]
                    merge_group["childRow"] += 1

                    item = Item()
                    item.update(data)

                    self.add_child(item, parent=merge_group)

                    # Set the version information
                    index = self.index(row_, 0, parent=merge_group_index)
                    self.set_version(index, last_version)

        for subset in single_asset_subsets:
            last_version = last_versions[subset["_id"]]
            if not last_version:
                continue

            data = subset.copy()
            data["subset"] = data["name"]

            group_name = subset["data"].get("subsetGroup")
            if process_only_single_asset:
                if self._grouping and group_name:
                    group = group_items[group_name]
                    parent = group
                    parent_index = self.createIndex(0, 0, group)
                    row_ = group["childRow"]
                    group["childRow"] += 1
                else:
                    parent = None
                    parent_index = QtCore.QModelIndex()
                    row_ = row
                    row += 1
            else:
                parent = None
                parent_index = QtCore.QModelIndex()
                row_ = row
                row += 1

            item = Item()
            item.update(data)

            self.add_child(item, parent=parent)

            # Set the version information
            index = self.index(row_, 0, parent=parent_index)
            self.set_version(index, last_version)

        self.endResetModel()

    def data(self, index, role):

        if not index.isValid():
            return

        if role == self.SortDescendingRole:
            item = index.internalPointer()
            if item.get("isGroup") or item.get("isMerged"):
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
            if item.get("isGroup") or item.get("isMerged"):
                # Ensure groups be on top when sorting by ascending order
                prefix = "0"
                order = item["order"]
            else:
                prefix = "1"
                order = str(super(SubsetsModel, self).data(
                    index, QtCore.Qt.DisplayRole
                ))
            return prefix + order

        if role == QtCore.Qt.DisplayRole:
            if index.column() == self.Columns.index("family"):
                # Show familyLabel instead of family
                item = index.internalPointer()
                return item.get("familyLabel", None)

        elif role == QtCore.Qt.DecorationRole:

            # Add icon to subset column
            if index.column() == self.Columns.index("subset"):
                item = index.internalPointer()
                if item.get("isGroup") or item.get("isMerged"):
                    return item["icon"]
                else:
                    return self._icons["subset"]

            # Add icon to family column
            if index.column() == self.Columns.index("family"):
                item = index.internalPointer()
                return item.get("familyIcon", None)

        return super(SubsetsModel, self).data(index, role)

    def flags(self, index):
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        # Make the version column editable
        if index.column() == self.Columns.index("version"):  # version column
            flags |= QtCore.Qt.ItemIsEditable

        return flags

    def headerData(self, section, orientation, role):
        """Remap column names to labels"""
        if role == QtCore.Qt.DisplayRole:
            if section < len(self.Columns):
                key = self.Columns[section]
                return self.column_labels_mapping.get(key) or key

        super(TreeModel, self).headerData(section, orientation, role)


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

    def filterAcceptsRow(self, row=0, parent=QtCore.QModelIndex()):

        if not self._families:
            return False

        model = self.sourceModel()
        index = model.index(row, 0, parent=parent)

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
