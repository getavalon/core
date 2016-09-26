"""Public API

Anything that is not defined here is **internal** and
unreliable for external use.

Motivation for api.py:
    Storing the API in a module, as opposed to in __init__.py, enables
    use of it internally.

    For example, from `pipeline.py`:
        >> from . import api
        >> api.do_this()

    The important bit is avoiding circular dependencies, where api.py
    is calling upon a module which in turn calls upon api.py.

"""

from . import schema

from .pipeline import (
    ls,
    root,

    register_root,
    register_host,
    register_plugins,

    deregister_plugins,

    registered_host,
    registered_root,
    fixture,
)

from .lib import (
    format_user_dir,
    format_shared_dir,
    format_version,

    find_latest_version,
    parse_version,
)

__all__ = [
    "schema",

    "ls",
    "root",

    "register_host",
    "register_plugins",

    "register_root",
    "registered_root",
    "registered_host",

    "deregister_plugins",

    "format_user_dir",
    "format_shared_dir",
    "format_version",

    "find_latest_version",
    "parse_version",

    "fixture",
]
