import sys

import unreal
from .. import api, schema

from ..lib import logger

self = sys.modules[__name__]
self._menu = "avalonue4"  # Unique name of menu

AVALON_CONTAINERS = "AvalonContainers"


def install(config):

    self._menu = api.Session["AVALON_LABEL"] + "menu"
    _register_callbacks()
    _register_events()


def _register_callbacks():
    """
    TODO: Implement callbacks if supported by UE4
    """
    pass


def _register_events():
    """
    TODO: Implement callbacks if supported by UE4
    """
    pass
