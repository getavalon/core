from ....vendor import qtawesome
from ....vendor.Qt import QtCore

from .... import io, api, style

GROUP_CONFIG = {}


def is_filtering_recursible():
    """Does Qt binding support recursive filtering for QSortFilterProxyModel ?

    (NOTE) Recursive filtering was introduced in Qt 5.10.

    """
    return hasattr(
        QtCore.QSortFilterProxyModel, "setRecursiveFilteringEnabled"
    )


def refresh_group_config():
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

    GROUP_CONFIG.clear()
    GROUP_CONFIG.update(groups)

    return groups


def get_active_group_config(asset_id, include_predefined=False):
    """Collect all active groups from each subset
    """
    predefineds = GROUP_CONFIG.copy()
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


def walk_hierarchy(item):
    """Recursively yield group item
    """
    for child in item.children():
        if child.get("isGroupItem"):
            yield child

        for _child in walk_hierarchy(child):
            yield _child
