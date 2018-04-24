import re
from ...vendor.Qt import QtCore


class FilterProxyModel(QtCore.QSortFilterProxyModel):
    """Filter model to where key column's value is in the filtered tags"""

    def __init__(self, *args, **kwargs):
        super(FilterProxyModel, self).__init__(*args, **kwargs)
        self._filter_outdated = False

    def filterAcceptsRow(self, row, parent):

        model = self.sourceModel()
        source_index = model.index(row,
                                   self.filterKeyColumn(),
                                   parent)

        # Always allow bottom entries (individual containers), since their
        # parent group hidden if it wouldn't have been validated.
        rows = model.rowCount(source_index)
        if not rows:
            return True

        # Filter by regex
        if not self.filterRegExp().isEmpty():
            pattern = re.escape(self.filterRegExp().pattern())

            if not self._matches(row, parent, pattern):
                # Also allow if any of the children matches
                if not any(self._matches(i, source_index, pattern)
                           for i in range(rows)):
                    return False

        if self._filter_outdated:
            # When filtering to outdated we filter the up to date entries
            # thus we "allow" them when they are outdated
            if not self._is_outdated(row, parent):
                return False

        return True

    def set_filter_outdated(self, state):
        """Set whether to show the outdated entries only."""
        state = bool(state)

        if state != self._filter_outdated:
            self._filter_outdated = bool(state)
            self.invalidateFilter()

    def _is_outdated(self, row, parent):
        """Return whether row is outdated.

        A row is considered outdated if it has "version" and "highest_version"
        data and in the internal data structure, and they are not of an
        equal value.

        """

        index = self.sourceModel().index(row, self.filterKeyColumn(), parent)

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

    def _matches(self, row, parent, pattern):
        """Return whether row matches regex pattern.

        Args:
            row (int): row number in model
            parent (QtCore.QModelIndex): parent index
            pattern (regex.pattern): pattern to check for in key

        Returns:
            bool

        """

        index = self.sourceModel().index(row, self.filterKeyColumn(), parent)
        key = self.sourceModel().data(index, self.filterRole())
        if re.search(pattern, key, re.IGNORECASE):
            return True
