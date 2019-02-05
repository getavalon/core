import os
import importlib
import logging
from bson.objectid import ObjectId
from ...vendor import qtawesome, six
from ...pipeline import (
    is_compatible_loader,
    _make_backwards_compatible_loader,
    IncompatibleLoaderError
)

FAMILY_ICON_COLOR = "#0091B2"
FAMILY_CONFIG = {}
log = logging.getLogger(__name__)


def get(config, name):
    """Get value from config with fallback to default"""
    # We assume the default fallback key in the config is `__default__`
    return config.get(name, config.get("__default__", None))


# Copied from cbloader.lib - few changes needed:
#     refresh_family_config
#         - added 'db' to args, replaced 'io' in code
#         TODO !!!These were set to default values, they worked with api.data,
#         that may make a conflits. Not sure what they change...
#             - default_state
#             - toggled

def refresh_family_config(db):
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
    project = db.find_one({"type": "project"},
                          projection={"config.families": True})

    assert project, "Project not found!"
    families = project['config'].get("families", [])
    families = {family['name']: family for family in families}

    # Check if any family state are being overwritten by the configuration
    # default_state = api.data.get("familiesStateDefault", True)
    # toggled = set(api.data.get("familiesStateToggled", []))
    default_state = True
    toggled = set()

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


'''
Copied from avalon.pipeline where few changes needed:
'''


# find_config
#     - added 'db' to args
#         - db.session replaced Session in code
def find_config(db):
    log.info("Finding configuration for project..")

    config = db.Session["AVALON_CONFIG"]

    if not config:
        raise EnvironmentError("No configuration found in "
                               "the project nor environment")

    log.info("Found %s, loading.." % config)
    return importlib.import_module(config)


# loaders_from_representation
#     - added 'db' to args
def loaders_from_representation(db, loaders, representation):
    """Return all compatible loaders for a representation."""
    context = get_representation_context(db, representation)
    return [l for l in loaders if is_compatible_loader(l, context)]


# get_representation_context
#     - added 'db' to args replaced 'io' in code
def get_representation_context(db, representation):
    """Return parenthood context for representation.

    Args:
        representation (str or io.ObjectId or dict): The representation id
            or full representation as returned by the database.

    Returns:
        dict: The full representation context.

    """

    assert representation is not None, "This is a bug"

    if isinstance(representation, (six.string_types, ObjectId)):
        representation = db.find_one(
            {"_id": ObjectId(str(representation))})

    version, subset, asset, project = db.parenthood(representation)

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
def load(db, Loader, representation, namespace=None, name=None, options=None,
         **kwargs):
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
    context = get_representation_context(db, representation)

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


def registered_root(db):
    return os.path.normpath(
        db.Session.get("AVALON_PROJECTS") or ""
    )
