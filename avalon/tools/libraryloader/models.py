import collections
import logging

from .. import TreeModel, Item
from .. import lib
from .... import style
from ....vendor import qtawesome

from ....vendor.Qt import QtCore, QtGui

log = logging.getLogger(__name__)


class TasksModel(TreeModel):
    """A model listing the tasks combined for a list of assets"""

    COLUMNS = ["name", "count"]

    def __init__(self, parent=None):
        super(TasksModel, self).__init__()
        self.db = parent.db
        self._num_assets = 0
        self._icons = {
            "__default__": qtawesome.icon(
                "fa.folder-o", color=style.colors.default
            )
        }

        self._get_task_icons()

    def _get_task_icons(self):
        # Get the project configured icons from database
        project = self.db.find_one({"type": "project"})
        tasks = project['config'].get('tasks', [])
        for task in tasks:
            icon_name = task.get("icon", None)
            if icon_name:
                icon = qtawesome.icon(
                    "fa.{}".format(icon_name),
                    color=style.colors.default
                )
                self._icons[task["name"]] = icon

    def set_assets(self, asset_ids):
        """Set assets to track by their database id

        Arguments:
            asset_ids (list): List of asset ids.

        """

        assets = list()
        for asset_id in asset_ids:
            asset = self.db.find_one(
                {"_id": asset_id, "type": "asset"}
            )
            assert asset, "Asset not found by id: {0}".format(asset_id)
            assets.append(asset)

        self._num_assets = len(assets)

        tasks = collections.Counter()
        for asset in assets:
            asset_tasks = asset.get("data", {}).get("tasks", [])
            tasks.update(asset_tasks)

        # If no asset tasks are defined, use the project tasks.
        if assets and not tasks:
            project = self.db.find_one({"type": "project"})
            tasks.update(
                [task["name"] for task in project["config"].get("tasks", [])]
            )

        self.clear()
        # delete empty strings from tasks
        del tasks[""]
        # let cleared task view if no tasks are available
        if len(tasks) == 0:
            return

        self.beginResetModel()

        default_icon = self._icons["__default__"]
        for task, count in sorted(tasks.items()):
            icon = self._icons.get(task, default_icon)

            item = Item({
                "name": task,
                "count": count,
                "icon": icon
            })

            self.add_child(item)

        self.endResetModel()

    def headerData(self, section, orientation, role):

        # Override header for count column to show amount of assets
        # it is listing the tasks for
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 1:  # count column
                    return "count ({0})".format(self._num_assets)

        return super(TasksModel, self).headerData(section, orientation, role)

    def data(self, index, role):

        if not index.isValid():
            return

        # Add icon to the first column
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return index.internalPointer()['icon']

        return super(TasksModel, self).data(index, role)


class AssetModel(TreeModel):
    """A model listing assets in the silo in the active project.

    The assets are displayed in a treeview, they are visually parented by
    a `visualParent` field in the database containing an `_id` to a parent
    asset.

    """

    COLUMNS = ["label"]
    Name = 0
    Deprecated = 2
    ObjectId = 3

    DocumentRole = QtCore.Qt.UserRole + 2
    ObjectIdRole = QtCore.Qt.UserRole + 3

    def __init__(self, parent):
        super(AssetModel, self).__init__(parent=parent)
        self.parent_widget = parent
        self.refresh()

    @property
    def db(self):
        return self.parent_widget.db

    def _add_hierarchy(self, parent=None):

        # Find the assets under the parent
        find_data = {
            "type": "asset"
        }
        if parent is None:
            find_data['$or'] = [
                {'data.visualParent': {'$exists': False}},
                {'data.visualParent': None}
            ]
        else:
            find_data["data.visualParent"] = parent['_id']

        assets = self.db.find(find_data).sort('name', 1)
        for asset in assets:
            # get label from data, otherwise use name
            data = asset.get("data", {})
            label = data.get("label", asset['name'])
            tags = data.get("tags", [])

            # store for the asset for optimization
            deprecated = "deprecated" in tags

            item = Item({
                "_id": asset['_id'],
                "name": asset["name"],
                "label": label,
                "type": asset['type'],
                "tags": ", ".join(tags),
                "deprecated": deprecated,
                "_document": asset
            })
            self.add_child(item, parent=parent)

            # Add asset's children recursively
            self._add_hierarchy(item)

    def refresh(self):
        """Refresh the data for the model."""

        self.clear()
        if (
            self.db.active_project() is None or
            self.db.active_project() == ''
        ):
            return
        self.beginResetModel()
        self._add_hierarchy(parent=None)
        self.endResetModel()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):

        if not index.isValid():
            return

        item = index.internalPointer()
        if role == QtCore.Qt.DecorationRole:        # icon

            column = index.column()
            if column == self.Name:

                # Allow a custom icon and custom icon color to be defined
                data = item["_document"]["data"]
                icon = data.get("icon", None)
                color = data.get("color", style.colors.default)

                if icon is None:
                    # Use default icons if no custom one is specified.
                    # If it has children show a full folder, otherwise
                    # show an open folder
                    has_children = self.rowCount(index) > 0
                    icon = "folder" if has_children else "folder-o"

                # Make the color darker when the asset is deprecated
                if item.get("deprecated", False):
                    color = QtGui.QColor(color).darker(250)

                try:
                    key = "fa.{0}".format(icon)  # font-awesome key
                    icon = qtawesome.icon(key, color=color)
                    return icon
                except Exception as exception:
                    # Log an error message instead of erroring out completely
                    # when the icon couldn't be created (e.g. invalid name)
                    log.error(exception)

                return

        if role == QtCore.Qt.ForegroundRole:        # font color
            if "deprecated" in item.get("tags", []):
                return QtGui.QColor(style.colors.light).darker(250)

        if role == self.ObjectIdRole:
            return item.get("_id", None)

        if role == self.DocumentRole:
            return item.get("_document", None)

        return super(AssetModel, self).data(index, role)



class SubsetsModel(TreeModel):
    COLUMNS = ["subset",
               "family",
               "version",
               "time",
               "author",
               "frames",
               "duration",
               "handles",
               "step"]

    def __init__(self, parent=None):
        super(SubsetsModel, self).__init__(parent=parent)

        self.db = parent.db
        self._asset_id = None
        self._icons = {
            "subset": qtawesome.icon("fa.file-o", color=style.colors.default)
        }

    def set_asset(self, asset_id):
        self._asset_id = asset_id
        self.refresh()

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        # Trigger additional edit when `version` column changed
        # because it also updates the information in other columns
        if index.column() == 2:
            item = index.internalPointer()
            parent = item["_id"]
            version = self.db.find_one({
                "name": value,
                "type": "version",
                "parent": parent
            })
            self.set_version(index, version)

        return super(SubsetsModel, self).setData(index, value, role)

    def set_version(self, index, version):
        """Update the version data of the given index.

        Arguments:
            version (dict) Version document in the database. """

        assert isinstance(index, QtCore.QModelIndex)
        if not index.isValid():
            return

        item = index.internalPointer()
        assert version['parent'] == item['_id'], ("Version does not "
                                                  "belong to subset")

        # Get the data from the version
        version_data = version.get("data", dict())

        # Compute frame ranges (if data is present)
        start = version_data.get("frameStart", None)
        end = version_data.get("frameEnd", None)
        handles = version_data.get("handles", None)
        if start is not None and end is not None:
            # Remove superfluous zeros from numbers (3.0 -> 3) to improve
            # readability for most frame ranges
            start_clean = ('%f' % start).rstrip('0').rstrip('.')
            end_clean = ('%f' % end).rstrip('0').rstrip('.')
            frames = "{0}-{1}".format(start_clean, end_clean)
            duration = end - start + 1
        else:
            frames = None
            duration = None

        family = version_data.get("families", [None])[0]
        family_config = lib.get(lib.FAMILY_CONFIG, family)

        item.update({
            "version": version['name'],
            "version_document": version,
            "author": version_data.get("author", None),
            "time": version_data.get("time", None),
            "family": family,
            "familyLabel": family_config.get("label", family),
            "familyIcon": family_config.get('icon', None),
            "frameStart": start,
            "frameEnd": end,
            "duration": duration,
            "handles": handles,
            "frames": frames,
            "step": version_data.get("step", None)
        })

    def refresh(self):

        self.clear()
        self.beginResetModel()
        if not self._asset_id:
            self.endResetModel()
            return

        row = 0
        for subset in self.db.find({
            "type": "subset",
            "parent": self._asset_id
        }):

            last_version = self.db.find_one({
                "type": "version",
                "parent": subset['_id']
            },
                sort=[("name", -1)]
            )
            if not last_version:
                # No published version for the subset
                continue

            data = subset.copy()
            data['subset'] = data['name']

            item = Item()
            item.update(data)

            self.add_child(item)

            # Set the version information
            index = self.index(row, 0, parent=QtCore.QModelIndex())
            self.set_version(index, last_version)

            row += 1

        self.endResetModel()

    def data(self, index, role):

        if not index.isValid():
            return

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 1:
                # Show familyLabel instead of family
                item = index.internalPointer()
                return item.get("familyLabel", None)

        if role == QtCore.Qt.DecorationRole:

            # Add icon to subset column
            if index.column() == 0:
                return self._icons['subset']

            # Add icon to family column
            if index.column() == 1:
                item = index.internalPointer()
                return item.get("familyIcon", None)

        return super(SubsetsModel, self).data(index, role)

    def flags(self, index):
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        # Make the version column editable
        if index.column() == 2:  # version column
            flags |= QtCore.Qt.ItemIsEditable

        return flags
