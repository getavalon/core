import os
import importlib
import logging
from bson.objectid import ObjectId
from ... import api, style
from ...vendor import qtawesome, six
from ...pipeline import (
    is_compatible_loader,
    _make_backwards_compatible_loader,
    IncompatibleLoaderError
)

FAMILY_ICON_COLOR = "#0091B2"
FAMILY_CONFIG_CACHE = {}
GROUP_CONFIG_CACHE = {}

log = logging.getLogger(__name__)


def get_family_cached_config(name):
    """Get value from config with fallback to default"""
    # We assume the default fallback key in the config is `__default__`
    config = FAMILY_CONFIG_CACHE
    return config.get(name, config.get("__default__", None))


def refresh_family_config_cache(dbcon):
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
    project = dbcon.find_one({"type": "project"},
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


def refresh_group_config_cache(dbcon):
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
    project = dbcon.find_one({"type": "project"},
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


def get_active_group_config(dbcon, asset_id, include_predefined=False):
    """Collect all active groups from each subset"""
    predefineds = GROUP_CONFIG_CACHE.copy()
    default_group_config = predefineds.pop("__default__")

    _orders = set([0])  # default order zero included
    for config in predefineds.values():
        _orders.add(config["order"])

    # Remap order to list index
    orders = sorted(_orders)

    # Collect groups from subsets
    group_names = set(dbcon.distinct("data.subsetGroup",
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


# `find_config` from `pipeline`
#     - added 'dbcon' to args
#         - dbcon.session replaced Session in code
def find_config(dbcon):
    log.info("Finding configuration for project..")

    config = dbcon.Session["AVALON_CONFIG"]

    if not config:
        raise EnvironmentError("No configuration found in "
                               "the project nor environment")

    log.info("Found %s, loading.." % config)
    return importlib.import_module(config)


# loaders_from_representation
#     - added 'dbcon' to args
def loaders_from_representation(dbcon, loaders, representation):
    """Return all compatible loaders for a representation."""
    context = get_representation_context(dbcon, representation)
    return [l for l in loaders if is_compatible_loader(l, context)]


# get_representation_context
#     - added 'dbcon' to args replaced 'io' in code
def get_representation_context(dbcon, representation):
    """Return parenthood context for representation.

    Args:
        representation (str or io.ObjectId or dict): The representation id
            or full representation as returned by the database.

    Returns:
        dict: The full representation context.

    """

    assert representation is not None, "This is a bug"

    if isinstance(representation, (six.string_types, ObjectId)):
        representation = dbcon.find_one(
            {"_id": ObjectId(str(representation))})

    version, subset, asset, project = dbcon.parenthood(representation)

    assert all([representation, version, subset, asset, project]), (
        "This is a bug"
    )

    context = {
        "project": project,
        "asset": asset,
        "subset": subset,
        "version": version,
        "representation": representation,
    }

    return context


# load
def load(
    dbcon, Loader, representation, namespace=None, name=None, options=None,
    **kwargs
):
    """Use Loader to load a representation.

    Args:
        Loader (Loader): The loader class to trigger.
        representation (str or io.ObjectId or dict): The representation id
            or full representation as returned by the database.
        namespace (str, Optional): The namespace to assign. Defaults to None.
        name (str, Optional): The name to assign. Defaults to subset name.
        options (dict, Optional): Additional options to pass on to the loader.

    Returns:
        The return of the `loader.load()` method.

    Raises:
        IncompatibleLoaderError: When the loader is not compatible with
            the representation.

    """

    Loader = _make_backwards_compatible_loader(Loader)
    context = get_representation_context(dbcon, representation)

    # Ensure the Loader is compatible for the representation
    if not is_compatible_loader(Loader, context):
        raise IncompatibleLoaderError("Loader {} is incompatible with "
                                      "{}".format(Loader.__name__,
                                                  context["subset"]["name"]))

    # Ensure options is a dictionary when no explicit options provided
    if options is None:
        options = kwargs.get("data", dict())  # "data" for backward compat

    assert isinstance(options, dict), "Options must be a dictionary"

    # Fallback to subset when name is None
    if name is None:
        name = context["subset"]["name"]

    log.info(
        "Running '%s' on '%s'" % (Loader.__name__, context["asset"]["name"])
    )

    loader = Loader(context)
    return loader.load(context, name, namespace, options)


def registered_root(dbcon):
    return os.path.normpath(
        dbcon.Session.get("AVALON_PROJECTS") or ""
    )
