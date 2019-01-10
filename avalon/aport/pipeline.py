import os
import importlib
from pyblish import api as pyblish
from avalon import api
import logging


log = logging.getLogger(__name__)

AVALON_CONFIG = os.environ["AVALON_CONFIG"]


def ls():
    pass


def reload_pipeline():
    """Attempt to reload pipeline at run-time.

    CAUTION: This is primarily for development and debugging purposes.

    """

    import importlib

    api.uninstall()

    for module in ("avalon.io",
                   "avalon.lib",
                   "avalon.pipeline",
                   "avalon.api",
                   "avalon.tools",

                   "avalon.tools.loader.app",
                   "avalon.tools.creator.app",
                   "avalon.tools.manager.app",

                   "avalon.aport",
                   "avalon.aport.pipeline",
                   "{}".format(AVALON_CONFIG)
                   ):
        log.info("Reloading module: {}...".format(module))
        module = importlib.import_module(module)
        reload(module)

    import avalon.aport
    api.install(avalon.aport)


def install(config):
    """Install Aport-specific functionality of avalon-core.

    This is where you install menus and register families, data
    and loaders into Aport.

    It is called automatically when installing via `api.install(avalon.aport)`.

    See the Maya equivalent for inspiration on how to implement this.

    """

    pyblish.register_host("aport")
    # Trigger install on the config's "aport" package
    config = find_host_config(config)

    if hasattr(config, "install"):
        config.install()

    log.info("config.aport installed")


def find_host_config(config):
    try:
        config = importlib.import_module(config.__name__ + ".aport")
    except ImportError as exc:
        if str(exc) != "No module name {}".format(
                config.__name__ + ".aport"):
            raise
        config = None

    return config


def uninstall(config):
    """Uninstall all tha was installed

    This is where you undo everything that was done in `install()`.
    That means, removing menus, deregistering families and  data
    and everything. It should be as though `install()` was never run,
    because odds are calling this function means the user is interested
    in re-installing shortly afterwards. If, for example, he has been
    modifying the menu or registered families.

    """
    config = find_host_config(config)
    if hasattr(config, "uninstall"):
        config.uninstall()

    pyblish.deregister_host("aport")
