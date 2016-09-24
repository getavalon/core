"""Public API

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .pipeline import (
    install,
    uninstall,
    ls,
    register_root as root,  # alias

    register_root,
    register_host,
    register_plugins,

    deregister_plugins,

    registered_host,
)

from .lib import (
    format_user_dir,
    format_shared_dir,
    format_version,

    find_latest_version,
    parse_version,
)

__all__ = [
    "install",
    "uninstall",
    "ls",
    "root",

    "register_host",
    "register_plugins",

    "register_root",
    "registered_host",

    "deregister_plugins",

    "format_user_dir",
    "format_shared_dir",
    "format_version",

    "find_latest_version",
    "parse_version",
]
