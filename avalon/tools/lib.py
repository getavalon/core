import os
import sys
import contextlib

from .. import io, api, style
from ..vendor import qtawesome

from ..vendor.Qt import QtWidgets, QtCore, QtGui

self = sys.modules[__name__]
self._jobs = dict()
self._path = os.path.dirname(__file__)


def resource(*path):
    path = os.path.join(self._path, "_res", *path)
    return path.replace("\\", "/")


@contextlib.contextmanager
def application():
    app = QtWidgets.QApplication.instance()

    if not app:
        print("Starting new QApplication..")
        app = QtWidgets.QApplication(sys.argv)
        yield app
        app.exec_()
    else:
        print("Using existing QApplication..")
        yield app


def defer(delay, func):
    """Append artificial delay to `func`

    This aids in keeping the GUI responsive, but complicates logic
    when producing tests. To combat this, the environment variable ensures
    that every operation is synchonous.

    Arguments:
        delay (float): Delay multiplier; default 1, 0 means no delay
        func (callable): Any callable

    """

    delay *= float(os.getenv("PYBLISH_DELAY", 1))
    if delay > 0:
        return QtCore.QTimer.singleShot(delay, func)
    else:
        return func()


def schedule(func, time, channel="default"):
    """Run `func` at a later `time` in a dedicated `channel`

    Given an arbitrary function, call this function after a given
    timeout. It will ensure that only one "job" is running within
    the given channel at any one time and cancel any currently
    running job if a new job is submitted before the timeout.

    """

    try:
        self._jobs[channel].stop()
    except (AttributeError, KeyError):
        pass

    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(func)
    timer.start(time)

    self._jobs[channel] = timer


@contextlib.contextmanager
def dummy():
    """Dummy context manager

    Usage:
        >> with some_context() if False else dummy():
        ..   pass

    """

    yield


def iter_model_rows(model,
                    column,
                    include_root=False):
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
def preserve_expanded_rows(tree_view,
                           column=0,
                           role=QtCore.Qt.DisplayRole):
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

    for index in iter_model_rows(model,
                                 column=column,
                                 include_root=False):
        if tree_view.isExpanded(index):
            value = index.data(role)
            expanded.add(value)

    try:
        yield
    finally:
        if not expanded:
            return

        for index in iter_model_rows(model,
                                     column=column,
                                     include_root=False):
            value = index.data(role)
            state = value in expanded
            if state:
                tree_view.expand(index)
            else:
                tree_view.collapse(index)


@contextlib.contextmanager
def preserve_selection(tree_view,
                       column=0,
                       role=QtCore.Qt.DisplayRole,
                       current_index=True):
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
        for index in iter_model_rows(model,
                                     column=column,
                                     include_root=False):

            value = index.data(role)
            state = value in selected
            if state:
                tree_view.scrollTo(index)  # Ensure item is visible
                selection_model.select(index, flags)

            if current_index_value and value == current_index_value:
                selection_model.setCurrentIndex(index,
                                                selection_model.NoUpdate)


FAMILY_ICON_COLOR = "#0091B2"
FAMILY_CONFIG_CACHE = {}
GROUP_CONFIG_CACHE = {}


def get_family_cached_config(name):
    """Get value from config with fallback to default"""
    # We assume the default fallback key in the config is `__default__`
    config = FAMILY_CONFIG_CACHE
    return config.get(name, config.get("__default__", None))


def refresh_family_config_cache():
    """Get the family configurations from the database

    The configuration must be stored on the project under `config`.
    For example:

    {
        "config": {
            "families": [
                {"name": "avalon.camera", label: "Camera", "icon": "photo"},
                {"name": "avalon.anim", label: "Animation", "icon": "male"},
            ]
        }
    }

    It is possible to override the default behavior and set specific families
    checked. For example we only want the families imagesequence  and camera
    to be visible in the Loader.

    # This will turn every item off
    api.data["familyStateDefault"] = False

    # Only allow the imagesequence and camera
    api.data["familyStateToggled"] = ["imagesequence", "camera"]

    """
    # Update the icons from the project configuration
    project = io.find_one({"type": "project"},
                          projection={"config.families": True})

    assert project, "Project not found!"
    families = project["config"].get("families", [])
    families = {family["name"]: family for family in families}

    # Check if any family state are being overwritten by the configuration
    default_state = api.data.get("familiesStateDefault", True)
    toggled = set(api.data.get("familiesStateToggled", []))

    # Replace icons with a Qt icon we can use in the user interfaces
    default_icon = qtawesome.icon("fa.folder", color=FAMILY_ICON_COLOR)
    for name, family in families.items():
        # Set family icon
        icon = family.get("icon", None)
        if icon:
            family["icon"] = qtawesome.icon("fa.{}".format(icon),
                                            color=FAMILY_ICON_COLOR)
        else:
            family["icon"] = default_icon

        # Update state
        state = not default_state if name in toggled else default_state
        family["state"] = state

    # Default configuration
    families["__default__"] = {"icon": default_icon}

    FAMILY_CONFIG_CACHE.clear()
    FAMILY_CONFIG_CACHE.update(families)

    return families


def refresh_group_config_cache():
    """Get subset group configurations from the database

    The 'group' configuration must be stored in the project `config` field.
    See schema `config-1.0.json`

    """

    # Subset group item's default icon and order
    default_group_icon = qtawesome.icon("fa.object-group",
                                        color=style.colors.default)
    default_group_config = {"icon": default_group_icon,
                            "order": 0}

    # Get pre-defined group name and apperance from project config
    project = io.find_one({"type": "project"},
                          projection={"config.groups": True})

    assert project, "Project not found!"
    group_configs = project["config"].get("groups", [])

    # Build pre-defined group configs
    groups = dict()
    for config in group_configs:
        name = config["name"]
        icon = "fa." + config.get("icon", "object-group")
        color = config.get("color", style.colors.default)
        order = float(config.get("order", 0))

        groups[name] = {"icon": qtawesome.icon(icon, color=color),
                        "order": order}

    # Default configuration
    groups["__default__"] = default_group_config

    GROUP_CONFIG_CACHE.clear()
    GROUP_CONFIG_CACHE.update(groups)

    return groups


def get_active_group_config(asset_id, include_predefined=False):
    """Collect all active groups from each subset"""
    predefineds = GROUP_CONFIG_CACHE.copy()
    default_group_config = predefineds.pop("__default__")

    _orders = set([0])  # default order zero included
    for config in predefineds.values():
        _orders.add(config["order"])

    # Remap order to list index
    orders = sorted(_orders)

    # Collect groups from subsets
    group_names = set(io.distinct("data.subsetGroup",
                                  {"type": "subset", "parent": asset_id}))
    if include_predefined:
        # Ensure all predefined group configs will be included
        group_names.update(predefineds.keys())

    groups = list()

    for name in group_names:
        # Get group config
        config = predefineds.get(name, default_group_config)
        # Base order
        remapped_order = orders.index(config["order"])

        data = {
            "name": name,
            "icon": config["icon"],
            "_order": remapped_order,
        }

        groups.append(data)

    # Sort by tuple (base_order, name)
    # If there are multiple groups in same order, will sorted by name.
    ordered = sorted(groups, key=lambda dat: (dat.pop("_order"), dat["name"]))

    total = len(ordered)
    order_temp = "%0{}d".format(len(str(total)))

    # Update sorted order to config
    for index, data in enumerate(ordered):
        order = index
        inverse_order = total - order

        data.update({
            # Format orders into fixed length string for groups sorting
            "order": order_temp % order,
            "inverseOrder": order_temp % inverse_order,
        })

    return ordered
