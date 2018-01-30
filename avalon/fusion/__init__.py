import importlib
from pyblish import api as pyblish
import fusionless.core as fu


def ls():
    """List containers from active Maya scene

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Maya; once loaded
    they are called 'containers'

    """

    # TODO: Do this without `fusionless` for less dependencies
    comp = fu.Comp()
    tools = comp.GetToolList(False).values()
    for tool in tools:
        if tool.ID in ["Loader"]:
            from .pipeline import parse_container
            container = parse_container(tool)
            yield container


def install(config):
    """Install Fusion-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(fusion)`.

    """

    # TODO: Register Fusion callbacks
    # TODO: Set project
    # TODO: Install Fusion menu (this is done with config .fu script actually)

    pyblish.register_host("fusion")

    # Trigger install on the config's "fusion" package
    try:
        config = importlib.import_module(config.__name__ + ".fusion")
    except ImportError:
        pass
    else:
        if hasattr(config, "install"):
            config.install()
