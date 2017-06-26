import re
from ...vendor.Qt import QtCore


class RecursiveSortFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Filters to the regex if any of the children matches allow parent"""

    def filterAcceptsRow(self, row, parent):

        regex = self.filterRegExp()
        if not regex.isEmpty():
            pattern = regex.pattern()
            pattern = re.escape(pattern)
            model = self.sourceModel()
            source_index = model.index(row, self.filterKeyColumn(), parent)
            if source_index.isValid():

                # Check current index itself
                key = model.data(source_index, self.filterRole())
                if re.search(pattern, key, re.IGNORECASE):
                    return True

                # Check children
                rows = model.rowCount(source_index)
                for i in range(rows):
                    if self.filterAcceptsRow(i, source_index):
                        return True

                # Otherwise filter it
                return False

        return super(RecursiveSortFilterProxyModel,
                     self).filterAcceptsRow(row, parent)


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
