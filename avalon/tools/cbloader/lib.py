from ...vendor import qtawesome, Qt
from ... import io, api, style

FAMILY_ICON_COLOR = "#0091B2"
FAMILY_CONFIG = {}
GROUP_CONFIG = {}


def get(config, name):
    """Get value from config with fallback to default"""
    # We assume the default fallback key in the config is `__default__`
    return config.get(name, config.get("__default__", None))


def is_filtering_recursible():
    """Does Qt binding support recursive filtering for QSortFilterProxyModel ?

    (NOTE) Recursive filtering was introduced in Qt 5.10.

    """
    return hasattr(Qt.QtCore.QSortFilterProxyModel,
                   "setRecursiveFilteringEnabled")


def refresh_family_config():
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
    families = project['config'].get("families", [])
    families = {family['name']: family for family in families}

    # Check if any family state are being overwritten by the configuration
    default_state = api.data.get("familiesStateDefault", True)
    toggled = set(api.data.get("familiesStateToggled", []))

    # Replace icons with a Qt icon we can use in the user interfaces
    default_icon = qtawesome.icon("fa.folder", color=FAMILY_ICON_COLOR)
    for name, family in families.items():
        # Set family icon
        icon = family.get("icon", None)
        if icon:
            family['icon'] = qtawesome.icon("fa.{}".format(icon),
                                            color=FAMILY_ICON_COLOR)
        else:
            family['icon'] = default_icon

        # Update state
        state = not default_state if name in toggled else default_state
        family["state"] = state

    # Default configuration
    families["__default__"] = {"icon": default_icon}

    FAMILY_CONFIG.clear()
    FAMILY_CONFIG.update(families)

    return families


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
