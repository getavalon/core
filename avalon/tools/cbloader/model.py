from ... import io, style
from ...vendor.Qt import QtCore
from ...vendor import qtawesome as qta

from ..projectmanager.model import (
    TreeModel,
    Node
)

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

    SortRole = QtCore.Qt.UserRole + 2

    def __init__(self, parent=None):
        super(SubsetsModel, self).__init__(parent=parent)
        self._asset_id = None
        self._sorter = None
        self._icons = {"subset": qta.icon("fa.file-o",
                                          color=style.colors.default)}
        # Subset group item's default icon and order
        self._default_group = {"icon": qta.icon("fa.object-group",
                                                color=style.colors.default),
                               "order": 0}

    def set_sorter(self, sorter):
        self._sorter = sorter

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

        family = version_data.get("families", [None])[0]
        family_config = lib.get(lib.FAMILY_CONFIG, family)

        node.update({
            "version": version['name'],
            "version_document": version,
            "author": version_data.get("author", None),
            "time": version_data.get("time", None),
            "family": family,
            "familyLabel": family_config.get("label", family),
            "familyIcon": family_config.get('icon', None),
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

        filter = {"type": "subset", "parent": self._asset_id}

        # Get pre-defined group name and apperance from project config
        group_configs = io.find_one(
            {"type": "project"}, {"config.groups": 1}
        )["config"].get("groups") or []

        # Build pre-defined group configs
        predefineds = dict()
        sort_orders = set([0])  # default order zero included
        for config in group_configs:
            name = config["name"]
            icon = "fa." + config.get("icon", "object-group")
            color = config.get("color", style.colors.default)
            order = float(config.get("order"))

            predefineds[name] = {"icon": qta.icon(icon, color=color),
                                 "order": order}
            sort_orders.add(order)

        # For ensuring positive order
        order_offset = abs(min(sort_orders)) + 1
        # For computing complement number for inverse order
        order_cap = max(sort_orders) + order_offset

        # Collect subset groups
        group_nodes = dict()
        for group_name in io.distinct("data.subsetGroup", filter):
            group = Node()
            config = predefineds.get(group_name, self._default_group)
            data = {
                "subset": group_name,
                "icon": config["icon"],
                "fixAscending": config["order"] + order_offset,
                "fixDescending": order_cap - config["order"] + order_offset,
                "isGroup": True,
            }
            group.update(data)
            group_nodes[group_name] = {"node": group,
                                       "childRow": 0}
            self.add_child(group)

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
            if group_name:
                group = group_nodes[group_name]
                parent = group["node"]
                parent_index = self.createIndex(0, 0, parent)
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

        if role == self.SortRole:
            node = index.internalPointer()
            descending = self._sorter.sortOrder()
            column = self.COLUMNS[self._sorter.sortColumn()]
            # This would make group items always be on top, and always in
            # descending order.
            if node.get("isGroup"):
                if descending:
                    order = ".%010.4f" % node["fixDescending"]
                else:
                    order = ".+%010.4f" % node["fixAscending"]
            else:
                # The `v` is for prefixing version number, so they won't
                # ordering with group items which were using digit to sort.
                order = ".+v" + str(node[column])

            return order

        return super(SubsetsModel, self).data(index, role)

    def flags(self, index):
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        # Make the version column editable
        if index.column() == 2:  # version column
            flags |= QtCore.Qt.ItemIsEditable

        return flags


class SubsetFilterProxyModel(QtCore.QSortFilterProxyModel):

    def filterAcceptsRow(self, row, parent):

        model = self.sourceModel()
        index = model.index(row,
                            self.filterKeyColumn(),
                            parent)
        node = index.internalPointer()
        if node.get("isGroup"):
            # Keep group in view
            return True
        else:
            return super(SubsetFilterProxyModel,
                         self).filterAcceptsRow(row, parent)


class FamiliesFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Filters to specified families"""

    def __init__(self, *args, **kwargs):
        super(FamiliesFilterProxyModel, self).__init__(*args, **kwargs)
        self._families = set()

    def familyFilter(self):
        return self._families

    def setFamiliesFilter(self, values):
        """Set the families to include"""
        assert isinstance(values, (tuple, list, set))
        self._families = set(values)
        self.invalidateFilter()

    def filterAcceptsRow(self, row=0, parent=QtCore.QModelIndex()):

        if not self._families:
            return False

        model = self.sourceModel()
        index = model.index(row, 0, parent=parent)

        # Ensure index is valid
        if not index.isValid() or index is None:
            return True

        # Get the node data and validate
        node = model.data(index, TreeModel.NodeRole)
        family = node.get("family", None)

        if not family:
            return True

        # We want to keep the families which are not in the list
        return family in self._families
