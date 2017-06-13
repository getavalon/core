from ..vendor.Qt import QtWidgets, QtCore
import logging

log = logging.getLogger(__name__)


class Node(dict):
    """A node that can be represented in a tree view.

    The node can store data just like a dictionary.

    >>> data = {"name": "John", "score": 10}
    >>> node = DictTreeNode(data)
    >>> assert node["name"] == "John"

    """
    def __init__(self, data=None):
        super(Node, self).__init__()

        self._children = list()
        self._parent = None

        if data is not None:
            assert isinstance(data, dict)
            self.update(data)

    def childCount(self):
        return len(self._children)

    def child(self, row):

        if row >= len(self._children):
            log.warning("Invalid row as child: {0}".format(row))
            return

        return self._children[row]

    def children(self):
        return self._children

    def parent(self):
        return self._parent

    def row(self):
        """
        Returns:
             int: Index of this node under parent"""
        if self._parent is not None:
            siblings = self.parent().children()
            return siblings.index(self)

    def addChild(self, child):
        """Add a child to this node"""
        child._parent = self
        self._children.append(child)


class TreeModel(QtCore.QAbstractItemModel):

    COLUMNS = list()
    NodeRole = QtCore.Qt.UserRole + 1

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self._root_node = Node()

    def rowCount(self, parent):
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self._root_node

        return node.childCount()

    def columnCount(self, parent):
        return len(self.COLUMNS)

    def data(self, index, role):

        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:

            node = index.internalPointer()
            column = index.column()

            key = self.COLUMNS[column]
            return node.get(key, None)

        if role == self.NodeRole:
            return index.internalPointer()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """Change the data on the nodes.

        Returns:
            bool: Whether the edit was successful
        """

        if index.isValid():
            if role == QtCore.Qt.EditRole:

                node = index.internalPointer()
                column = index.column()
                key = self.COLUMNS[column]
                node[key] = value

                # must return true if successful
                return True

        return False

    def setColumns(self, keys):
        assert isinstance(keys, (list, tuple))
        self.COLUMNS = keys

    def headerData(self, section, orientation, role):

        if role == QtCore.Qt.DisplayRole:
            if section < len(self.COLUMNS):
                return self.COLUMNS[section]

        super(TreeModel, self).headerData(section, orientation, role)

    def flags(self, index):
        return (
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsSelectable
        )

    def parent(self, index):

        node = index.internalPointer()
        parent_node = node.parent()

        # If it has no parents we return invalid
        if parent_node == self._root_node or not parent_node:
            return QtCore.QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def index(self, row, column, parent):
        """Return index for row/column under parent"""

        if not parent.isValid():
            parentNode = self._root_node
        else:
            parentNode = parent.internalPointer()

        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def add_child(self, node, parent=None):
        if parent is None:
            parent = self._root_node

        parent.addChild(node)

    def column_name(self, column):
        """Return column key by index"""

        if column < len(self.COLUMNS):
            return self.COLUMNS[column]

    def clear(self):
        self.beginResetModel()
        self._root_node = Node()
        self.endResetModel()
