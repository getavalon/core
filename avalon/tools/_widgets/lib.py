import contextlib
from . import QtCore
from . import io
from .._models.lib import get


def _iter_model_rows(model, column, include_root=False):
    """Iterate over all row indices in a model"""
    indices = [QtCore.QModelIndex()]  # start iteration at root

    for index in indices:

        # Add children to the iterations
        child_rows = model.rowCount(index)
        for child_row in range(child_rows):
            child_index = model.index(child_row, column, index)
            indices.append(child_index)

        if not include_root and not index.isValid():
            continue

        yield index


@contextlib.contextmanager
def preserve_expanded_rows(tree_view, column=0, role=QtCore.Qt.DisplayRole):
    """Preserves expanded row in QTreeView by column's data role.

    This function is created to maintain the expand vs collapse status of
    the model items. When refresh is triggered the items which are expanded
    will stay expanded and vise versa.

    Arguments:
        tree_view (QWidgets.QTreeView): the tree view which is
            nested in the application
        column (int): the column to retrieve the data from
        role (int): the role which dictates what will be returned

    Returns:
        None

    """

    model = tree_view.model()

    expanded = set()

    for index in _iter_model_rows(model, column=column, include_root=False):
        if tree_view.isExpanded(index):
            value = index.data(role)
            expanded.add(value)

    try:
        yield
    finally:
        if not expanded:
            return

        for index in _iter_model_rows(
            model, column=column, include_root=False
        ):
            value = index.data(role)
            state = value in expanded
            if state:
                tree_view.expand(index)
            else:
                tree_view.collapse(index)


@contextlib.contextmanager
def preserve_selection(
    tree_view, column=0, role=QtCore.Qt.DisplayRole, current_index=True
):
    """Preserves row selection in QTreeView by column's data role.

    This function is created to maintain the selection status of
    the model items. When refresh is triggered the items which are expanded
    will stay expanded and vise versa.

        tree_view (QWidgets.QTreeView): the tree view nested in the application
        column (int): the column to retrieve the data from
        role (int): the role which dictates what will be returned

    Returns:
        None

    """

    model = tree_view.model()
    selection_model = tree_view.selectionModel()
    flags = selection_model.Select | selection_model.Rows

    if current_index:
        current_index_value = tree_view.currentIndex().data(role)
    else:
        current_index_value = None

    selected_rows = selection_model.selectedRows()
    if not selected_rows:
        yield
        return

    selected = set(row.data(role) for row in selected_rows)
    try:
        yield
    finally:
        if not selected:
            return

        # Go through all indices, select the ones with similar data
        for index in _iter_model_rows(
            model, column=column, include_root=False
        ):
            value = index.data(role)
            state = value in selected
            if state:
                tree_view.scrollTo(index)  # Ensure item is visible
                selection_model.select(index, flags)

            if current_index_value and value == current_index_value:
                tree_view.setCurrentIndex(index)


def _list_project_silos():
    """List the silos from the project's configuration"""
    # old way: silos = io.distinct("silo")
    # new, Backwards compatible way to get all silos from DB:
    silos = [s['name'] for s in io.find({"type": "asset", "silo": None})]
    silos_old = io.distinct("silo")
    for silo in silos_old:
        if silo not in silos and silo is not None:
            silos.append(silo)

    if not silos:
        project = io.find_one({"type": "project"})
        log.warning("Project '%s' has no active silos", project['name'])

    return list(sorted(silos))
