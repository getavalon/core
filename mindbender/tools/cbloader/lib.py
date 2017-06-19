from ... import api
from ... import io
from ...vendor import six


def get_representation_context(representation):
    """Return the full context for a representation.
    
    The full context includes all parent information required for the Loader
    to process a specific representation.
    
    """

    if isinstance(representation, (six.string_types, io.ObjectId)):
        representation = io.find_one({"_id": io.ObjectId(str(representation))})
    else:
        raise TypeError("Representation is not correct type.")

    version, subset, asset, project = io.parenthood(representation)

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


def is_compatible_loader(Loader, context):
    """Return whether a loader is compatible with a context."""
    families = context['version']['data']['families']
    representation = context['representation']
    has_family = ("*" in Loader.families or
                  any(family in Loader.families for family in families))
    has_representation = ("*" in Loader.representations or
                          representation["name"] in Loader.representations)
    return has_family and has_representation


def iter_loaders(representation):
    """Yield all compatible loaders for a representation."""

    context = get_representation_context(representation)
    for Loader in api.discover(api.Loader):
        if is_compatible_loader(Loader, context):
            yield Loader


def run_loader(Loader,
               representation):
    """Run the loader on representation.
    
    Args:
        Loader (api.Loader): The loader class to run.
        representation (str): The representation database id.
    
    """

    context = get_representation_context(representation)
    if not is_compatible_loader(Loader, context):
        raise RuntimeError("Loader is not compatible.")

    host = api.registered_host()
    return host.load(Loader, representation=representation)
