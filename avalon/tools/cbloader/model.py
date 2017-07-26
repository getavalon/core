from ... import io
from ..projectmanager.model import (
    TreeModel,
    Node
)
from ..projectmanager import style
from ...vendor.Qt import QtCore
from ...vendor import qtawesome as qta


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
        self._asset_id = None
        self._icons = {"subset": qta.icon("fa.file-o", color=style.default)}

    def set_asset(self, asset_id):
        self._asset_id = asset_id
        self.refresh()

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        # Trigger additional edit when `version` column changed
        # because it also updates the information in other columns
        if index.column() == 2:
            node = index.internalPointer()
            parent = node["_id"]
            version = io.find_one({"name": value,
                                   "type": "version",
                                   "parent": parent})
            print node, version
            self.set_version(index, version)

        return super(SubsetsModel, self).setData(index, value, role)

    def set_version(self, index, version):
        """Update the version data of the given index.
        
        Arguments:
            version (dict) Version document in the database. """

        assert isinstance(index, QtCore.QModelIndex)
        if not index.isValid():
            return

        node = index.internalPointer()
        assert version['parent'] == node['_id'], ("Version does not "
                                                  "belong to subset")

        # Get the data from the version
        version_data = version.get("data", dict())

        # Compute frame ranges (if data is present)
        start = version_data.get("startFrame", None)
        end = version_data.get("endFrame", None)
        handles = version_data.get("handles", None)
        if start is not None and end is not None:
            frames = "{0}-{1}".format(start, end)
            duration = end - start + 1
        else:
            frames = None
            duration = None

        node.update({
            "version": version['name'],
            "version_document": version,
            "author": version_data.get("author", None),
            "time": version_data.get("time", None),
            "family": version_data.get("families", ["<unknown>"])[0],
            "startFrame": start,
            "endFrame": end,
            "duration": duration,
            "handles": handles,
            "frames": frames,
            "step": version_data.get("step", None)
        })

    def refresh(self):

        self.clear()
        self.beginResetModel()
        if not self._asset_id:
            return

        row = 0
        for subset in io.find({"type": "subset",
                               "parent": self._asset_id}):

            last_version = io.find_one({"type": "version",
                                        "parent": subset['_id']},
                                       sort=[("name", -1)])
            if not last_version:
                # No published version for the subset
                continue

            data = subset.copy()
            data['subset'] = data['name']

            node = Node()
            node.update(data)

            self.add_child(node)

            # Set the version information
            index = self.index(row, 0, parent=QtCore.QModelIndex())
            self.set_version(index, last_version)

            row += 1

        self.endResetModel()

    def data(self, index, role):

        # Add icon to subset column
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return self._icons['subset']

        return super(SubsetsModel, self).data(index, role)

    def flags(self, index):
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        # Make the version column editable
        if index.column() == 2:  # version column
            flags |= QtCore.Qt.ItemIsEditable

        return flags
