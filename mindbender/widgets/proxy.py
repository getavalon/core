from ..vendor.Qt import QtCore, QtGui, QtWidgets
import re


class ExactMatchesFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Filter model to where key column's value is in the filtered tags"""

    def __init__(self, *args, **kwargs):
        super(ExactMatchesFilterProxyModel, self).__init__(*args, **kwargs)
        self._filters = set()

    def setFilters(self, filters):
        self._filters = set(filters)

    def filterAcceptsRow(self, source_row, source_parent):

        # No filter
        if not self._filters:
            return True

        else:
            model = self.sourceModel()
            column = self.filterKeyColumn()
            idx = model.index(source_row, column, source_parent)
            data = model.data(idx, self.filterRole())
            if data in self._filters:
                return True
            else:
                return False


class RecursiveSortFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Filters to the regex if any of the children matches allow parent"""
    def filterAcceptsRow(self, row, parent):

        regex = self.filterRegExp()
        if not regex.isEmpty():
            pattern = regex.pattern()
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
