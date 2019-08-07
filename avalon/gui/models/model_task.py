import collections

from ...vendor import qtawesome
from ...vendor.Qt import QtCore

from ... import io
from .. import style
from .. import TreeModel, Node


class TaskModel(TreeModel):
    """A model listing the tasks combined for a list of assets"""

    COLUMNS = ["name", "count"]

    def __init__(self):
        super(TaskModel, self).__init__()
        self._num_assets = 0
        self._icons = {
            "__default__": qtawesome.icon(
                "fa.male", color=style.colors.default
            )
        }

        self._get_task_icons()

    def _get_task_icons(self):
        # Get the project configured icons from database
        project = io.find_one({"type": "project"})
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
            asset = io.find_one({"_id": asset_id, "type": "asset"})
            assert asset, "Asset not found by id: {0}".format(asset_id)
            assets.append(asset)

        self._num_assets = len(assets)

        tasks = collections.Counter()
        for asset in assets:
            asset_tasks = asset.get("data", {}).get("tasks", [])
            tasks.update(asset_tasks)

        self.clear()
        self.beginResetModel()

        default_icon = self._icons["__default__"]
        for task, count in sorted(tasks.items()):
            icon = self._icons.get(task, default_icon)

            node = Node({
                "name": task,
                "count": count,
                "icon": icon
            })

            self.add_child(node)

        self.endResetModel()

    def headerData(self, section, orientation, role):

        # Override header for count column to show amount of assets
        # it is listing the tasks for
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 1:  # count column
                    return "count ({0})".format(self._num_assets)

        return super(TaskModel, self).headerData(section, orientation, role)

    def data(self, index, role):

        if not index.isValid():
            return

        # Add icon to the first column
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return index.internalPointer()['icon']

        return super(TaskModel, self).data(index, role)
