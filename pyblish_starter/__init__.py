import os
import pyblish.api

from .pipeline import (
    time,
    format_private_dir,
)
	
def register_plugins():
    # Register accompanying plugins
    from . import plugins
    plugin_path = os.path.dirname(plugins.__file__)
    pyblish.api.register_plugin_path(plugin_path)


def setup():
	register_plugins()


__all__ = [
    "time",
    "setup",
    "register_plugins",
    "format_private_dir",
]
