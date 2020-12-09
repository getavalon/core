import copy

from ... import style
from ...vendor.Qt import QtCore, QtGui
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

    doc_fetched = QtCore.Signal()
    refreshed = QtCore.Signal(bool)

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
    not_last_master_brush = QtGui.QBrush(QtGui.QColor(254, 121, 121))

    # Should be minimum of required asset document keys
    asset_doc_projection = {
        "name": 1,
        "label": 1
    }
    # Should be minimum of required subset document keys
    subset_doc_projection = {
        "name": 1,
        "parent": 1,
        "schema": 1,
        "families": 1,
        "data.subsetGroup": 1
    }

    def __init__(
        self,
        dbcon,
        groups_config,
        family_config_cache,
        grouping=True,
        parent=None,
        asset_doc_projection=None,
        subset_doc_projection=None
    ):
        super(SubsetsModel, self).__init__(parent=parent)

        self.dbcon = dbcon

        # Projections for Mongo queries
        # - let ability to modify them if used in tools that require more than
        #   defaults
        if asset_doc_projection:
            self.asset_doc_projection = asset_doc_projection

        if subset_doc_projection:
            self.subset_doc_projection = subset_doc_projection

        self.asset_doc_projection = asset_doc_projection
        self.subset_doc_projection = subset_doc_projection

        self.columns_index = dict(
            (key, idx) for idx, key in enumerate(self.Columns)
        )
        self._asset_ids = None

        self.groups_config = groups_config
        self.family_config_cache = family_config_cache
        self._sorter = None
        self._grouping = grouping
        self._icons = {
            "subset": qtawesome.icon("fa.file-o", color=style.colors.default)
        }

        self._doc_fetching_thread = None
        self._doc_fetching_stop = False
        self._doc_payload = {}

        self.doc_fetched.connect(self.on_doc_fetched)

    def set_assets(self, asset_ids):
        self._asset_ids = asset_ids
        self.refresh()

    def set_grouping(self, state):
        self._grouping = state
        self.on_doc_fetched()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        # Trigger additional edit when `version` column changed
        # because it also updates the information in other columns
        if index.column() == self.columns_index["version"]:
            item = index.internalPointer()
            parent = item["_id"]
            if isinstance(value, MasterVersionType):
                versions = list(self.dbcon.find({
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
                version = self.dbcon.find_one({
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

        assert version["parent"] == item["_id"], (
            "Version does not belong to subset"
        )

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
        family_config = self.family_config_cache.family_config(family)

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

    def _fetch(self):
        asset_docs = self.dbcon.find(
            {
                "type": "asset",
                "_id": {"$in": self._asset_ids}
            },
            self.asset_doc_projection
        )
        asset_docs_by_id = {
            asset_doc["_id"]: asset_doc
            for asset_doc in asset_docs
        }

        subset_docs_by_id = {}
        subset_docs = self.dbcon.find(
            {
                "type": "subset",
                "parent": {"$in": self._asset_ids}
            },
            self.subset_doc_projection
        )
        for subset in subset_docs:
            if self._doc_fetching_stop:
                return
            subset_docs_by_id[subset["_id"]] = subset

        subset_ids = list(subset_docs_by_id.keys())
        _pipeline = [
            # Find all versions of those subsets
            {"$match": {
                "type": "version",
                "parent": {"$in": subset_ids}
            }},
            # Sorting versions all together
            {"$sort": {"name": 1}},
            # Group them by "parent", but only take the last
            {"$group": {
                "_id": "$parent",
                "_version_id": {"$last": "$_id"},
                "name": {"$last": "$name"},
                "type": {"$last": "$type"},
                "data": {"$last": "$data"},
                "locations": {"$last": "$locations"},
                "schema": {"$last": "$schema"}
            }}
        ]
        last_versions_by_subset_id = dict()
        for doc in self.dbcon.aggregate(_pipeline):
            if self._doc_fetching_stop:
                return
            doc["parent"] = doc["_id"]
            doc["_id"] = doc.pop("_version_id")
            last_versions_by_subset_id[doc["parent"]] = doc

        master_versions = self.dbcon.find({
            "type": "master_version",
            "parent": {"$in": subset_ids}
        })
        missing_versions = []
        for master_version in master_versions:
            version_id = master_version["version_id"]
            if version_id not in last_versions_by_subset_id:
                missing_versions.append(version_id)

        missing_versions_by_id = {}
        if missing_versions:
            missing_version_docs = self.dbcon.find({
                "type": "version",
                "_id": {"$in": missing_versions}
            })
            missing_versions_by_id = {
                missing_version_doc["_id"]: missing_version_doc
                for missing_version_doc in missing_version_docs
            }

        for master_version in master_versions:
            version_id = master_version["version_id"]
            subset_id = master_version["parent"]

            version_doc = last_versions_by_subset_id.get(subset_id)
            if version_doc is None:
                version_doc = missing_versions_by_id.get(version_id)
                if version_doc is None:
                    continue

            master_version["data"] = version_doc["data"]
            master_version["name"] = MasterVersionType(version_doc["name"])
            # Add information if master version is from latest version
            master_version["is_from_latest"] = version_id == version_doc["_id"]

            last_versions_by_subset_id[subset_id] = master_version

        self._doc_payload = {
            "asset_docs_by_id": asset_docs_by_id,
            "subset_docs_by_id": subset_docs_by_id,
            "last_versions_by_subset_id": last_versions_by_subset_id
        }
        self.doc_fetched.emit()

    def fetch_subset_and_version(self):
        """Query all subsets and latest versions from aggregation
        (NOTE) The returned version documents are NOT the real version
            document, it's generated from the MongoDB's aggregation so
            some of the first level field may not be presented.
        """
        self._doc_payload = {}
        self._doc_fetching_stop = False
        self._doc_fetching_thread = lib.create_qthread(self._fetch)
        self._doc_fetching_thread.start()

    def stop_fetch_thread(self):
        if self._doc_fetching_thread is not None:
            self._doc_fetching_stop = True
            while self._doc_fetching_thread.isRunning():
                pass

    def refresh(self):
        self.stop_fetch_thread()
        self.clear()

        if not self._asset_ids:
            return

        self.fetch_subset_and_version()

    def on_doc_fetched(self):
        self.clear()
        self.beginResetModel()

        asset_docs_by_id = self._doc_payload.get(
            "asset_docs_by_id"
        )
        subset_docs_by_id = self._doc_payload.get(
            "subset_docs_by_id"
        )
        last_versions_by_subset_id = self._doc_payload.get(
            "last_versions_by_subset_id"
        )
        if (
            asset_docs_by_id is None
            or subset_docs_by_id is None
            or last_versions_by_subset_id is None
            or len(self._asset_ids) == 0
        ):
            self.endResetModel()
            self.refreshed.emit(False)
            return

        self._fill_subset_items(
            asset_docs_by_id, subset_docs_by_id, last_versions_by_subset_id
        )

    def create_multiasset_group(
        self, subset_name, asset_ids, subset_counter, parent_item=None
    ):
        subset_color = self.merged_subset_colors[
            subset_counter % len(self.merged_subset_colors)
        ]
        merge_group = Item()
        merge_group.update({
            "subset": "{} ({})".format(subset_name, len(asset_ids)),
            "isMerged": True,
            "childRow": 0,
            "subsetColor": subset_color,
            "assetIds": list(asset_ids),
            "icon": qtawesome.icon(
                "fa.circle",
                color="#{0:02x}{1:02x}{2:02x}".format(*subset_color)
            )
        })

        subset_counter += 1
        self.add_child(merge_group, parent_item)

        return merge_group

    def _fill_subset_items(
        self, asset_docs_by_id, subset_docs_by_id, last_versions_by_subset_id
    ):
        _groups_tuple = self.groups_config.split_subsets_for_groups(
            subset_docs_by_id.values(), self._grouping
        )
        groups, subset_docs_without_group, subset_docs_by_group = _groups_tuple

        group_item_by_name = {}
        for group_data in groups:
            group_name = group_data["name"]
            group_item = Item()
            group_item.update({
                "subset": group_name,
                "isGroup": True,
                "childRow": 0
            })
            group_item.update(group_data)

            self.add_child(group_item)

            group_item_by_name[group_name] = {
                "item": group_item,
                "index": self.index(group_item.row(), 0)
            }

        subset_counter = 0
        for group_name, subset_docs_by_name in subset_docs_by_group.items():
            parent_item = group_item_by_name[group_name]["item"]
            parent_index = group_item_by_name[group_name]["index"]
            for subset_name in sorted(subset_docs_by_name.keys()):
                subset_docs = subset_docs_by_name[subset_name]
                asset_ids = [
                    subset_doc["parent"] for subset_doc in subset_docs
                ]
                if len(subset_docs) > 1:
                    _parent_item = self.create_multiasset_group(
                        subset_name, asset_ids, subset_counter, parent_item
                    )
                    _parent_index = self.index(
                        _parent_item.row(), 0, parent_index
                    )
                    subset_counter += 1
                else:
                    _parent_item = parent_item
                    _parent_index = parent_index

                for subset_doc in subset_docs:
                    asset_id = subset_doc["parent"]

                    data = copy.deepcopy(subset_doc)
                    data["subset"] = subset_name
                    data["asset"] = asset_docs_by_id[asset_id]["name"]

                    last_version = last_versions_by_subset_id.get(
                        subset_doc["_id"]
                    )
                    data["last_version"] = last_version

                    item = Item()
                    item.update(data)
                    self.add_child(item, _parent_item)

                    index = self.index(item.row(), 0, _parent_index)
                    self.set_version(index, last_version)

        for subset_name in sorted(subset_docs_without_group.keys()):
            subset_docs = subset_docs_without_group[subset_name]
            asset_ids = [subset_doc["parent"] for subset_doc in subset_docs]
            parent_item = None
            parent_index = None
            if len(subset_docs) > 1:
                parent_item = self.create_multiasset_group(
                    subset_name, asset_ids, subset_counter
                )
                parent_index = self.index(parent_item.row(), 0)
                subset_counter += 1

            for subset_doc in subset_docs:
                asset_id = subset_doc["parent"]

                data = copy.deepcopy(subset_doc)
                data["subset"] = subset_name
                data["asset"] = asset_docs_by_id[asset_id]["name"]

                last_version = last_versions_by_subset_id.get(
                    subset_doc["_id"]
                )
                data["last_version"] = last_version

                item = Item()
                item.update(data)
                self.add_child(item, parent_item)

                index = self.index(item.row(), 0, parent_index)
                self.set_version(index, last_version)

        self.endResetModel()
        self.refreshed.emit(True)

    def data(self, index, role):
        if not index.isValid():
            return

        if role == self.SortDescendingRole:
            item = index.internalPointer()
            if item.get("isGroup"):
                # Ensure groups be on top when sorting by descending order
                prefix = "2"
                order = item["order"]
            else:
                if item.get("isMerged"):
                    prefix = "1"
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
                if item.get("isMerged"):
                    prefix = "1"
                else:
                    prefix = "2"
                order = str(super(SubsetsModel, self).data(
                    index, QtCore.Qt.DisplayRole
                ))
            return prefix + order

        if role == QtCore.Qt.DisplayRole:
            if index.column() == self.columns_index["family"]:
                # Show familyLabel instead of family
                item = index.internalPointer()
                return item.get("familyLabel", None)

        elif role == QtCore.Qt.DecorationRole:

            # Add icon to subset column
            if index.column() == self.columns_index["subset"]:
                item = index.internalPointer()
                if item.get("isGroup") or item.get("isMerged"):
                    return item["icon"]
                else:
                    return self._icons["subset"]

            # Add icon to family column
            if index.column() == self.columns_index["family"]:
                item = index.internalPointer()
                return item.get("familyIcon", None)

        elif role == QtCore.Qt.ForegroundRole:
            item = index.internalPointer()
            version_doc = item.get("version_document")
            if version_doc and version_doc.get("type") == "master_version":
                if not version_doc["is_from_latest"]:
                    return self.not_last_master_brush

        return super(SubsetsModel, self).data(index, role)

    def flags(self, index):
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        # Make the version column editable
        if index.column() == self.columns_index["version"]:
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
        index = model.index(row, self.filterKeyColumn(), parent)
        item = index.internalPointer()
        if item.get("isGroup"):
            return self.filter_accepts_group(index, model)
        return super(
            SubsetFilterProxyModel, self
        ).filterAcceptsRow(row, parent)


class FamiliesFilterProxyModel(GroupMemberFilterProxyModel):
    """Filters to specified families"""

    def __init__(self, family_config_cache, *args, **kwargs):
        super(FamiliesFilterProxyModel, self).__init__(*args, **kwargs)
        self._families = set()
        self.family_config_cache = family_config_cache

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
            family_config = self.family_config_cache.family_config(name)
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
