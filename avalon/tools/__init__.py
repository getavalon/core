import sys

# Backwards compatibility
# Support `from avalon.tools import cbloader`
from . import (
    sceneinventory as cbsceneinventory,
    loader as cbloader,
)

from .lib import (
    application,
)

# Support `import avalon.tools.cbloader`
sys.modules[__name__ + ".cbsceneinventory"] = cbsceneinventory
sys.modules[__name__ + ".cbloader"] = cbloader

__all__ = [
    "application",

    "cbsceneinventory",
    "cbloader",
]
