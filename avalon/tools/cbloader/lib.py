from ...vendor import qtawesome
from ... import io

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
    if not project:
        raise RuntimeError("Project not found")
    families = project['config'].get("families", [])
    families = {family['name']: family for family in families}

    # Replace icons with a Qt icon we can use in the user interfaces
    default_icon = qtawesome.icon("fa.folder", color=FAMILY_ICON_COLOR)
    for name, family in families.items():
        icon = family.get("icon", None)
        if icon:
            family['icon'] = qtawesome.icon("fa.{}".format(icon),
                                            color=FAMILY_ICON_COLOR)
        else:
            family['icon'] = default_icon

    # Default configuration
    families["__default__"] = {"icon": default_icon}

    FAMILY_CONFIG.clear()
    FAMILY_CONFIG.update(families)

    return families
