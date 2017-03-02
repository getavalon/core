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

import logging

from . import schema

from .pipeline import (
    install,
    uninstall,

    ls,
    search,

    Loader,
    discover_loaders,

    register_root,
    register_data,
    register_host,
    register_format,
    register_silo,
    register_family,
    register_loader_path,
    register_plugins,
    register_app,

    registered_host,
    registered_families,
    registered_loader_paths,
    registered_formats,
    registered_data,
    registered_root,
    registered_silos,
    registered_apps,

    deregister_plugins,
    deregister_format,
    deregister_family,
    deregister_data,
    deregister_loader_path,

    any_representation,

    fixture,
)

from .lib import (
    format_staging_dir,
    format_shared_dir,
    format_version,

    time,

    find_latest_version,
    parse_version,
)

logging.basicConfig()

__all__ = [
    "install",
    "uninstall",

    "schema",

    "ls",
    "search",

    "Loader",
    "discover_loaders",

    "register_host",
    "register_data",
    "register_format",
    "register_silo",
    "register_family",
    "register_loader_path",
    "register_plugins",
    "register_root",
    "register_app",

    "registered_root",
    "registered_loader_paths",
    "registered_host",
    "registered_families",
    "registered_formats",
    "registered_data",
    "registered_silos",
    "registered_apps",

    "deregister_plugins",
    "deregister_format",
    "deregister_family",
    "deregister_data",
    "deregister_loader_path",

    "format_staging_dir",
    "format_shared_dir",
    "format_version",

    "find_latest_version",
    "parse_version",

    "time",

    "any_representation",

    "fixture",
]
