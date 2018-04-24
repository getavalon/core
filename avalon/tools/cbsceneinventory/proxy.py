import re
from ...vendor.Qt import QtCore


class RecursiveSortFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Filters to the regex if any of the children matches allow parent"""

    def filterAcceptsRow(self, row, parent):
        if not self.filterRegExp().isEmpty():

            pattern = re.escape(self.filterRegExp().pattern())
            model = self.sourceModel()
            source_index = model.index(row, self.filterKeyColumn(), parent)

            if source_index.isValid():

                # Check current index itself
                key = model.data(source_index, self.filterRole())
                if re.search(pattern, key, re.IGNORECASE):
                    return True

                rows = model.rowCount(source_index)
                if not rows:
                    # Display item if parent matches
                    return True

                return any([self.filterAcceptChildRow(i, source_index, pattern)
                            for i in range(rows)])

        return super(RecursiveSortFilterProxyModel,
                     self).filterAcceptsRow(row, parent)

    def filterAcceptChildRow(self, row, parent, pattern):
        """
        Check if child row matches regex
        Args:
            row (int): row number in model
            parent (QtCore.QModelIndex): parent index item
            pattern (regex.pattern): pattern to check for in key

        Returns:
            bool

        """

        idx = self.sourceModel().index(row, self.filterKeyColumn(), parent)
        key = self.sourceModel().data(idx, self.filterRole())
        if re.search(pattern, key, re.IGNORECASE):
            return True


class FilterProxyModel(RecursiveSortFilterProxyModel):
    """Filter model to where key column's value is in the filtered tags"""

    def __init__(self, *args, **kwargs):
        super(FilterProxyModel, self).__init__(*args, **kwargs)
        self._enabled = False

    def set_filter_enabled(self, state):
        state = bool(state)

        if state != self._enabled:
            self._enabled = bool(state)
            self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):

        state = super(FilterProxyModel, self).filterAcceptsRow(source_row,
                                                               source_parent)
        # If not allowed by parent class then disallow it, otherwise
        # continue filtering
        if not state:
            return False

        if not self._enabled:
            return True

        model = self.sourceModel()
        column = self.filterKeyColumn()
        index = model.index(source_row, column, source_parent)

        # The scene contents are grouped by "representation", e.g. the same
        # "representation" loaded twice is grouped under the same header.
        # Since the version check filters these parent groups we skip that
        # check for the individual children.
        has_parent = index.parent().isValid()
        if has_parent:
            return True

        # Filter to those that have the different version numbers
        node = index.internalPointer()
        version = node.get("version", None)
        highest = node.get("highest_version", None)

        # Always allow indices that have no version data at all
        if version is None and highest is None:
            return True

        # If either a version or highest is present but not the other
        # consider the item invalid
        if version is None or highest is None:
            return False

        return version != highest
