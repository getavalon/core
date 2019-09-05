import logging

from ....vendor import qtawesome
from ....vendor.Qt import QtCore, QtGui

from .... import io, style
from . import TreeModel, Node

log = logging.getLogger(__name__)


class AssetModel(TreeModel):
    """ Displaying assets in hierarchical tree by visualParent.

    The assets are displayed in a treeview, they are visually parented by
    a `visualParent` field in the database containing an `_id` to a parent
    asset.

    Entities with `visualParent` set to None/null/nil are used as top items.
    """

    COLUMNS = ["label"]
    Name = 0
    Deprecated = 2
    ObjectId = 3

    DocumentRole = QtCore.Qt.UserRole + 2
    ObjectIdRole = QtCore.Qt.UserRole + 3

    def __init__(self, parent=None):
        super(AssetModel, self).__init__(parent=parent)
        self.refresh()

    def _add_hierarchy(self, parent=None, assets={}):

        # Find the assets under the parent
        current_assets = []
        if parent is None:
            db_assets = io.find({
                "type": "asset"
            }).sort('name', 1)
            assets = {}
            for asset in db_assets:
                parent_id = asset.get("data", {}).get("visualParent")
                if parent_id:
                    if parent_id not in assets:
                        assets[parent_id] = []
                    assets[parent_id].append(asset)
                else:
                    current_assets.append(asset)
        else:
            if parent["_id"] in assets:
                current_assets = assets.pop(parent["_id"])

        for asset in current_assets:
            # get label from data, otherwise use name
            data = asset.get("data", {})
            label = data.get("label", asset['name'])
            tags = data.get("tags", [])

            # store for the asset for optimization
            deprecated = "deprecated" in tags

            node = Node({
                "_id": asset['_id'],
                "name": asset["name"],
                "label": label,
                "type": asset['type'],
                "tags": ", ".join(tags),
                "deprecated": deprecated,
                "_document": asset
            })
            self.add_child(node, parent=parent)

            # Add asset's children recursively
            if asset['_id'] in assets:
                assets = self._add_hierarchy(node, assets)

        return assets

    def refresh(self):
        """Refresh the data for the model."""

        self.clear()
        self.beginResetModel()
        self._add_hierarchy(parent=None)
        self.endResetModel()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return

        node = index.internalPointer()
        if role == QtCore.Qt.DecorationRole:        # icon

            column = index.column()
            if column == self.Name:

                # Allow a custom icon and custom icon color to be defined
                data = node["_document"]["data"]
                icon = data.get("icon", None)
                color = data.get("color", style.colors.default)

                if icon is None:
                    # Use default icons if no custom one is specified.
                    # If it has children show a full folder, otherwise
                    # show an open folder
                    has_children = self.rowCount(index) > 0
                    icon = "folder" if has_children else "folder-o"

                # Make the color darker when the asset is deprecated
                if node.get("deprecated", False):
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
            if "deprecated" in node.get("tags", []):
                return QtGui.QColor(style.colors.light).darker(250)

        if role == self.ObjectIdRole:
            return node.get("_id", None)

        if role == self.DocumentRole:
            return node.get("_document", None)

        return super(AssetModel, self).data(index, role)
