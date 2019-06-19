from . import QtCore
from . import qtawesome, io, style
from . import TreeModel, Node


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

    def __init__(self, silo=None, parent=None):
        super(AssetModel, self).__init__(parent=parent)

        self._silo = None

        if silo is not None:
            self.set_silo(silo, refresh=True)

    def set_silo(self, silo, refresh=True):
        """Set the root path to the ItemType root."""
        self._silo = silo
        try:
            self.silo_asset = io.find_one(
                {'$and': [
                    {'type': 'asset'},
                    {'name': silo},
                    {'silo': None}
                ]}
            )
        except Exception:
            self.silo_asset = None
        if refresh:
            self.refresh()

    def _add_hierarchy(self, parent=None):

        # Find the assets under the parent
        find_data = {
            "type": "asset",
            "silo": self._silo,
        }
        if parent is None:
            # if not a parent find all that are parented to the project
            # or do *not* have a visualParent field at all
            if self.silo_asset is None:
                find_data['$or'] = [
                    {'data.visualParent': {'$exists': False}},
                    {'data.visualParent': None}
                ]
            else:
                find_data['data.visualParent'] = self.silo_asset['_id']

        else:
            find_data["data.visualParent"] = parent['_id']

        assets = io.find(find_data).sort('name', 1)
        for asset in assets:
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
            self._add_hierarchy(node)

    def refresh(self):
        """Refresh the data for the model."""

        self.clear()
        self.beginResetModel()
        if self._silo:
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
