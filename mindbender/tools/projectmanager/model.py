from ...vendor.Qt import QtCore
from ...vendor import qtawesome as qta
from ...widgets.tree import TreeModel, Node
from ...widgets import style
from ... import io
from collections import Counter


class TasksModel(TreeModel):
    """A model listing the tasks combined for a list of assets"""

    COLUMNS = ["name", "count"]

    def __init__(self):
        super(TasksModel, self).__init__()
        self._num_assets = 0
        self._icons = {
            "folder": qta.icon("fa.folder-o", color=style.default)
        }

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

        tasks = Counter()
        for asset in assets:
            tasks.update(asset.get("tasks", []))

        self.clear()
        self.beginResetModel()

        for task, count in sorted(tasks.items()):
            node = Node({
                "name": task,
                "count": count
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

        return super(TasksModel, self).headerData(section, orientation, role)

    def data(self, index, role):

        # Add icon to the first column
        if role == QtCore.Qt.DecorationRole:
            column = index.column()
            if column == 0:
                return self._icons["folder"]

        return super(TasksModel, self).data(index, role)
