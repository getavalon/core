import collections
import logging

from .. import models as tools_models
from ..loader import model as loader_models
from ..models import TreeModel, Item
from . import lib
from ..lib import MasterVersionType
from ... import style

from ...vendor import qtawesome
from ...vendor.Qt import QtCore

log = logging.getLogger(__name__)


class TasksModel(tools_models.TasksModel):
    """A model listing the tasks combined for a list of assets."""

    Columns = ["name", "count"]

    def __init__(self, dbcon, parent=None):
        self.dbcon = dbcon
        super(TasksModel, self).__init__(parent=parent)

    def _get_task_icons(self):
        # Get the project configured icons from database
        project = self.dbcon.find_one({"type": "project"})
        tasks = project["config"].get("tasks", [])
        for task in tasks:
            icon_name = task.get("icon", None)
            if icon_name:
                icon = qtawesome.icon(
                    "fa.{}".format(icon_name),
                    color=style.colors.default
                )
                self._icons[task["name"]] = icon

    def set_assets(self, asset_ids=[], asset_entities=None):
        """Set assets to track by their database id.

        Arguments:
            asset_ids (list): List of asset ids.
            asset_entities (list): List of asset entities from MongoDB.
        """
        assets = list()
        if asset_entities is not None:
            assets = asset_entities
        else:
            # prepare filter query
            or_query = [{"_id": asset_id} for asset_id in asset_ids]
            _filter = {"type": "asset", "$or": or_query}

            # find assets in db by query
            assets = [asset for asset in self.dbcon.find_one(_filter)]
            db_assets_ids = [asset["_id"] for asset in assets]

            # check if all assets were found
            not_found = [
                str(a_id) for a_id in asset_ids if a_id not in db_assets_ids
            ]

            assert not not_found, "Assets not found by id: {0}".format(
                ", ".join(not_found)
            )

        self._num_assets = len(assets)

        tasks = collections.Counter()
        for asset in assets:
            asset_tasks = asset.get("data", {}).get("tasks", [])
            tasks.update(asset_tasks)

        self.clear()
        self.beginResetModel()

        default_icon = self._icons["__default__"]

        if not tasks:
            no_task_icon = self._icons["__no_task__"]
            item = Item({
                "name": "No task",
                "count": 0,
                "icon": no_task_icon,
                "enabled": False,
            })

            self.add_child(item)

        else:
            for task, count in sorted(tasks.items()):
                icon = self._icons.get(task, default_icon)

                item = Item({
                    "name": task,
                    "count": count,
                    "icon": icon
                })

                self.add_child(item)

        self.endResetModel()


class AssetModel(tools_models.AssetModel):
    """A model listing assets in the silo in the active project.

    The assets are displayed in a treeview, they are visually parented by
    a `visualParent` field in the database containing an `_id` to a parent
    asset.

    """

    def __init__(self, dbcon, parent=None):
        self.dbcon = dbcon
        super(AssetModel, self).__init__(parent=parent)

    def refresh(self):
        """Refresh the data for the model."""

        self.clear()
        if (
            self.dbcon.active_project() is None or
            self.dbcon.active_project() == ""
        ):
            return

        self.beginResetModel()

        db_assets = []
        silos = None

        # Get all assets sorted by name
        db_assets = self.dbcon.find({"type": "asset"}).sort("name", 1)
        silos = db_assets.distinct("silo") or None
        if silos and None in silos:
            silos = None

        # Group the assets by their visual parent's id
        assets_by_parent = collections.defaultdict(list)
        for asset in db_assets:
            parent_id = (
                asset.get("data", {}).get("visualParent") or
                asset.get("silo")
            )
            assets_by_parent[parent_id].append(asset)

        # Build the hierarchical tree items recursively
        self._add_hierarchy(
            assets_by_parent,
            parent=None,
            silos=silos
        )

        self.endResetModel()


class SubsetsModel(loader_models.SubsetsModel):

    def __init__(self, dbcon, grouping=True, parent=None):
        self.dbcon = dbcon
        super(SubsetsModel, self).__init__(grouping=grouping, parent=parent)

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        # Trigger additional edit when `version` column changed
        # because it also updates the information in other columns
        if index.column() == self.Columns.index("version"):
            item = index.internalPointer()
            parent = item["_id"]
            if isinstance(value, MasterVersionType):
                version = self.dbcon.find_one({
                    "type": "master_version",
                    "parent": parent
                })
                _version = self.dbcon.find_one({
                    "_id": version["version_id"],
                    "type": "version"
                })
                version["data"] = _version["data"]
                version["name"] = _version["name"]

            else:
                version = self.dbcon.find_one({
                    "name": value,
                    "type": "version",
                    "parent": parent
                })
            self.set_version(index, version)

        # Use super of TreeModel not SubsetsModel from loader!!
        # - he would do the same but with current io context
        return super(loader_models.SubsetsModel, self).setData(
            index, value, role
        )

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

        version_value = version["name"]

        item.update({
            "version": version_value,
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
            result = lib.get_active_group_config(self.dbcon, asset_id)
            if result:
                active_groups.extend(result)

        filtered_subsets = [
            sub for sub in self.dbcon.find({
                "type": "subset", "parent": {"$in": self._asset_ids}
            })
        ]

        asset_entities = {}
        for asset_id in self._asset_ids:
            asset_ent = self.dbcon.find_one({"_id": asset_id})
            asset_entities[asset_id] = asset_ent

        # Collect last versions
        last_versions = {}
        for subset in filtered_subsets:
            master_version = self.dbcon.find_one({
                "type": "master_version",
                "parent": subset["_id"]
            })
            if master_version:
                _version = self.dbcon.find_one({
                    "_id": master_version["version_id"]
                })
                master_version["data"] = _version["data"]
                master_version["name"] = MasterVersionType(_version["name"])
                last_versions[subset["_id"]] = master_version
                continue

            last_version = self.dbcon.find_one({
                "type": "version",
                "parent": subset["_id"]
            }, sort=[("name", -1)])
            # No published version for the subset
            last_versions[subset["_id"]] = last_version

        # Prepare data if is selected more than one asset
        process_only_single_asset = True
        merge_subsets = False
        if len(self._asset_ids) >= 2:
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


class FamiliesFilterProxyModel(loader_models.FamiliesFilterProxyModel):
    """Filters to specified families"""

    def __init__(self, *args, **kwargs):
        super(FamiliesFilterProxyModel, self).__init__(*args, **kwargs)

    def filterAcceptsRow(self, row=0, parent=QtCore.QModelIndex()):

        if not self._families:
            return False

        model = self.sourceModel()
        index = model.index(row, 0, parent=parent)

        # Ensure index is valid
        if not index.isValid() or index is None:
            return True

        # Get the node data and validate
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
