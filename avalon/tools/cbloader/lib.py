import importlib

from ...vendor import qtawesome
from ... import io, pipeline

FAMILY_ICON_COLOR = "#0091B2"
FAMILY_CONFIG = {}


def get(config, name):
    """Get value from config with fallback to default"""
    # We assume the default fallback key in the config is `__default__`
    return config.get(name, config.get("__default__", None))


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

    """
    # Update the icons from the project configuration
    project = io.find_one({"type": "project"},
                          projection={"config.families": True})

    assert project, "Project not found!"
    families = project['config'].get("families", [])
    families = {family['name']: family for family in families}

    # Get all family states based on the config
    family_states = get_family_filters(families)
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
        family.update(family_states[name])

    # Default configuration
    families["__default__"] = {"icon": default_icon}

    FAMILY_CONFIG.clear()
    FAMILY_CONFIG.update(families)

    return families


def get_family_filters(families):
    """Set the family states based on host settings

    This function has no effect if the lib module or the function in not present
    in the registered config.

    Args:
        families (iterable): collection of family names, example:
                             ["polly.imagesequence", "polly.camera_abc"]

    Returns:
        dict: collection of family settings
    """

    # Find host's lib module in the registered config
    host = pipeline.registered_host()
    host_name = host.__name__.rsplit(".", 1)[-1]

    config = pipeline.registered_config()
    config_name = config.__name__.split(".", 1)[0]
    config_lib_module = "{}.{}.lib".format(config_name, host_name)

    # Check if host is compatible
    try:
        lib = importlib.import_module(config_lib_module)
    except (ValueError, TypeError, RuntimeError):
        print("Configuration has no module called {0} or "
              "{0}.lib".format(host_name))
        return {}

    if not hasattr(lib, "set_family_filter"):
        return {}

    new_states = {name: {"state": lib.set_family_filter(name)}
                  for name in families}

    return new_states
