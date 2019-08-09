from . import GroupMemberFilterProxyModel


class SubsetFilterProxyModel(GroupMemberFilterProxyModel):

    def filterAcceptsRow(self, row, parent):

        model = self.sourceModel()
        index = model.index(row,
                            self.filterKeyColumn(),
                            parent)
        node = index.internalPointer()
        if node.get("isGroup"):
            return self.filter_accepts_group(index, model)
        else:
            return super(SubsetFilterProxyModel,
                         self).filterAcceptsRow(row, parent)
