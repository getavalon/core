from . import QtCore
from . import qtawesome, style, io
from . import Node, TreeModel
from . import lib

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

    SortAscendingRole = QtCore.Qt.UserRole + 2
    SortDescendingRole = QtCore.Qt.UserRole + 3

    def __init__(self, grouping=True, parent=None):
        super(SubsetsModel, self).__init__(parent=parent)
        self._asset_id = None
        self._sorter = None
        self._grouping = grouping
        self._icons = {"subset": qtawesome.icon("fa.file-o",
                                          color=style.colors.default)}

    def set_asset(self, asset_id):
        self._asset_id = asset_id
        self.refresh()

    def set_grouping(self, state):
        self._grouping = state
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
            # Remove superfluous zeros from numbers (3.0 -> 3) to improve
            # readability for most frame ranges
            start_clean = ('%f' % start).rstrip('0').rstrip('.')
            end_clean = ('%f' % end).rstrip('0').rstrip('.')
            frames = "{0}-{1}".format(start_clean, end_clean)
            duration = end - start + 1
        else:
            frames = None
            duration = None

        families = version_data.get("families", [None])
        family = families[0]
        family_config = lib.get(lib.FAMILY_CONFIG, family)

        node.update({
            "version": version['name'],
            "version_document": version,
            "author": version_data.get("author", None),
            "time": version_data.get("time", None),
            "family": family,
            "familyLabel": family_config.get("label", family),
            "familyIcon": family_config.get('icon', None),
            "families": set(families),
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
            self.endResetModel()
            return

        asset_id = self._asset_id

        active_groups = lib.get_active_group_config(asset_id)

        # Generate subset group nodes
        group_nodes = dict()

        if self._grouping:
            for data in active_groups:
                name = data.pop("name")
                group = Node()
                group.update({"subset": name, "isGroup": True, "childRow": 0})
                group.update(data)

                group_nodes[name] = group
                self.add_child(group)

        filter = {"type": "subset", "parent": asset_id}

        # Process subsets
        row = len(group_nodes)
        for subset in io.find(filter):

            last_version = io.find_one({"type": "version",
                                        "parent": subset["_id"]},
                                       sort=[("name", -1)])
            if not last_version:
                # No published version for the subset
                continue

            data = subset.copy()
            data["subset"] = data["name"]

            group_name = subset["data"].get("subsetGroup")
            if self._grouping and group_name:
                group = group_nodes[group_name]
                parent = group
                parent_index = self.createIndex(0, 0, group)
                row_ = group["childRow"]
                group["childRow"] += 1
            else:
                parent = None
                parent_index = QtCore.QModelIndex()
                row_ = row
                row += 1

            node = Node()
            node.update(data)

            self.add_child(node, parent=parent)

            # Set the version information
            index = self.index(row_, 0, parent=parent_index)
            self.set_version(index, last_version)

        self.endResetModel()

    def data(self, index, role):

        if not index.isValid():
            return

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 1:
                # Show familyLabel instead of family
                node = index.internalPointer()
                return node.get("familyLabel", None)

        if role == QtCore.Qt.DecorationRole:

            # Add icon to subset column
            if index.column() == 0:
                node = index.internalPointer()
                if node.get("isGroup"):
                    return node["icon"]
                else:
                    return self._icons["subset"]

            # Add icon to family column
            if index.column() == 1:
                node = index.internalPointer()
                return node.get("familyIcon", None)

        if role == self.SortDescendingRole:
            node = index.internalPointer()
            if node.get("isGroup"):
                # Ensure groups be on top when sorting by descending order
                prefix = "1"
                order = node["inverseOrder"]
            else:
                prefix = "0"
                order = str(super(SubsetsModel,
                                  self).data(index, QtCore.Qt.DisplayRole))
            return prefix + order

        if role == self.SortAscendingRole:
            node = index.internalPointer()
            if node.get("isGroup"):
                # Ensure groups be on top when sorting by ascending order
                prefix = "0"
                order = node["order"]
            else:
                prefix = "1"
                order = str(super(SubsetsModel,
                                  self).data(index, QtCore.Qt.DisplayRole))
            return prefix + order

        return super(SubsetsModel, self).data(index, role)

    def flags(self, index):
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        # Make the version column editable
        if index.column() == 2:  # version column
            flags |= QtCore.Qt.ItemIsEditable

        return flags
