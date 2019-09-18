from . import TreeModel
from .model_item import Item
from .. import lib
from .... import style
from ....vendor import qtawesome as awesome
from ....vendor.Qt import QtCore


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
            "subset": awesome.icon("fa.file-o", color=style.colors.default)
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
