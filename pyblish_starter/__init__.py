"""Public API

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .pipeline import (
    ls,
    install,
    uninstall,

    register_host,
    register_plugins,

    registered_host,
)

from .lib import (
    format_private_dir,
    format_public_dir,
    format_version,
)

__all__ = [
    "ls",
    "install",
    "uninstall",

    "register_host",
    "register_plugins",

    "registered_host",

    "format_private_dir",
    "format_public_dir",
    "format_version",
]
