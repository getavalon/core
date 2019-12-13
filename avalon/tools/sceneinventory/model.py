import logging

from collections import defaultdict

from ... import api, io, style
from ...vendor.Qt import QtCore, QtGui
from ...vendor import qtawesome

from .. import lib as tools_lib
from ..models import TreeModel, Item

from . import lib


class InventoryModel(TreeModel):
    """The model for the inventory"""

    Columns = ["Name", "version", "count", "family", "loader", "objectName"]

    OUTDATED_COLOR = QtGui.QColor(235, 30, 30)
    CHILD_OUTDATED_COLOR = QtGui.QColor(200, 160, 30)
    GRAYOUT_COLOR = QtGui.QColor(160, 160, 160)

    UniqueRole = QtCore.Qt.UserRole + 2     # unique label role

    def __init__(self, parent=None):
        super(InventoryModel, self).__init__(parent)
        self.log = logging.getLogger(self.__class__.__name__)

        self._hierarchy_view = False

    def data(self, index, role):

        if not index.isValid():
            return

        item = index.internalPointer()

        if role == QtCore.Qt.FontRole:
            # Make top-level entries bold
            if item.get("isGroupNode"):  # group-item
                font = QtGui.QFont()
                font.setBold(True)
                return font

        if role == QtCore.Qt.ForegroundRole:
            # Set the text color to the OUTDATED_COLOR when the
            # collected version is not the same as the highest version
            key = self.Columns[index.column()]
            outdated = (lambda n: n.get("version") != n.get("highest_version"))
            if key == "version":  # version
                if item.get("isGroupNode"):  # group-item
                    if outdated(item):
                        return self.OUTDATED_COLOR

                    if self._hierarchy_view:
                        # If current group is not outdated, check if any
                        # outdated children.
                        for _node in lib.walk_hierarchy(item):
                            if outdated(_node):
                                return self.CHILD_OUTDATED_COLOR
                else:

                    if self._hierarchy_view:
                        # Although this is not a group item, we still need
                        # to distinguish which one contain outdated child.
                        for _node in lib.walk_hierarchy(item):
                            if outdated(_node):
                                return self.CHILD_OUTDATED_COLOR.darker(150)

                    return self.GRAYOUT_COLOR

            if key == "Name" and not item.get("isGroupNode"):
                return self.GRAYOUT_COLOR

        # Add icons
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                # Override color
                color = item.get("color", style.colors.default)
                if item.get("isGroupNode"):  # group-item
                    return qtawesome.icon("fa.folder", color=color)
                else:
                    return qtawesome.icon("fa.file-o", color=color)

            if index.column() == 3:
                # Family icon
                return item.get("familyIcon", None)

        if role == self.UniqueRole:
            return item["representation"] + item.get("objectName", "<none>")

        return super(InventoryModel, self).data(index, role)

    def set_hierarchy_view(self, state):
        """Set whether to display subsets in hierarchy view."""
        state = bool(state)

        if state != self._hierarchy_view:
            self._hierarchy_view = state

    def refresh(self, selected=None):
        """Refresh the model"""

        host = api.registered_host()
        items = host.ls()

        self.clear()

        if self._hierarchy_view and selected:

            if not hasattr(host.pipeline, "update_hierarchy"):
                # If host doesn't support hierarchical containers, then
                # cherry-pick only.
                self.add_items((item for item in items
                                if item["objectName"] in selected))

            # Update hierarchy info for all containers
            items_by_name = {item["objectName"]: item
                             for item in host.pipeline.update_hierarchy(items)}

            selected_items = set()

            def walk_children(names):
                """Select containers and extend to chlid containers"""
                for name in [n for n in names if n not in selected_items]:
                    selected_items.add(name)
                    item = items_by_name[name]
                    yield item

                    for child in walk_children(item["children"]):
                        yield child

            items = list(walk_children(selected))  # Cherry-picked and extended

            # Cut unselected upstream containers
            for item in items:
                if not item.get("parent") in selected_items:
                    # Parent not in selection, this is root item.
                    item["parent"] = None

            parents = [self._root_item]

            # The length of `items` array is the maximum depth that a
            # hierarchy could be.
            # Take this as an easiest way to prevent looping forever.
            maximum_loop = len(items)
            count = 0
            while items:
                if count > maximum_loop:
                    self.log.warning("Maximum loop count reached, possible "
                                     "missing parent node.")
                    break

                _parents = list()
                for parent in parents:
                    _unparented = list()

                    def _children():
                        """Child item provider"""
                        for item in items:
                            if item.get("parent") == parent.get("objectName"):
                                # (NOTE)
                                # Since `self._root_node` has no "objectName"
                                # entry, it will be paired with root item if
                                # the value of key "parent" is None, or not
                                # having the key.
                                yield item
                            else:
                                # Not current parent's child, try next
                                _unparented.append(item)

                    self.add_items(_children(), parent)

                    items[:] = _unparented

                    # Parents of next level
                    for group_node in parent.children():
                        _parents += group_node.children()

                parents[:] = _parents
                count += 1

        else:
            self.add_items(items)

    def add_items(self, items, parent=None):
        """Add the items to the model.

        The items should be formatted similar to `api.ls()` returns, an item
        is then represented as:
            {"filename_v001.ma": [full/filename/of/loaded/filename_v001.ma,
                                  full/filename/of/loaded/filename_v001.ma],
             "nodetype" : "reference",
             "node": "referenceNode1"}

        Note: When performing an additional call to `add_items` it will *not*
            group the new items with previously existing item groups of the
            same type.

        Args:
            items (generator): the items to be processed as returned by `ls()`
            parent (Item, optional): Set this item as parent for the added
              items when provided. Defaults to the root of the model.

        Returns:
            node.Item: root node which has children added based on the data
        """

        self.beginResetModel()

        # Group by representation
        grouped = defaultdict(list)
        for item in items:
            grouped[item["representation"]].append(item)

        # Add to model
        for representation_id, group_items in sorted(grouped.items()):

            # Get parenthood per group
            representation = io.find_one({
                "_id": io.ObjectId(representation_id)
            })
            version = io.find_one({"_id": representation["parent"]})
            subset = io.find_one({"_id": version["parent"]})
            asset = io.find_one({"_id": subset["parent"]})

            # Get the primary family
            no_family = ""
            if subset["schema"] == "avalon-core:subset-3.0":
                families = subset["data"]["families"]
                prim_family = families[0] if families else no_family
            else:
                prim_family = version["data"].get("family")
                if not prim_family:
                    families = version["data"].get("families")
                    prim_family = families[0] if families else no_family

            # Get the label and icon for the family if in configuration
            family_config = tools_lib.get_family_cached_config(prim_family)
            family = family_config.get("label", prim_family)
            family_icon = family_config.get("icon", None)

            # Store the highest available version so the model can know
            # whether current version is currently up-to-date.
            highest_version = io.find_one({
                "type": "version",
                "parent": version["parent"]
            }, sort=[("name", -1)])

            # create the group header
            group_node = Item()
            group_node["Name"] = "%s_%s: (%s)" % (asset["name"],
                                                  subset["name"],
                                                  representation["name"])
            group_node["representation"] = representation_id
            group_node["version"] = version["name"]
            group_node["highest_version"] = highest_version["name"]
            group_node["family"] = family
            group_node["familyIcon"] = family_icon
            group_node["count"] = len(group_items)
            group_node["isGroupNode"] = True

            self.add_child(group_node, parent=parent)

            for item in group_items:
                item_node = Item()
                item_node.update(item)

                # store the current version on the item
                item_node["version"] = version["name"]

                # Remapping namespace to item name.
                # Noted that the name key is capital "N", by doing this, we
                # can view namespace in GUI without changing container data.
                item_node["Name"] = item["namespace"]

                self.add_child(item_node, parent=group_node)

        self.endResetModel()

        return self._root_item
