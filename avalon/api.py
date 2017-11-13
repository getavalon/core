"""Public application programming interface

The following members are public and reliable.
That is to say, anything **not** defined here is **internal**
and likely **unreliable** for use outside of the codebase itself.

|
|

"""

from . import schema

from .pipeline import (
    install,
    uninstall,

    Loader,
    Creator,
    discover,
    Session,

    # Deprectated
    Session as session,

    on,
    after,
    before,
    emit,

    publish,
    create,
    load,
    update,
    remove,

    update_current_context,
    get_representation_path,
    loaders_from_representation,

    register_root,
    register_host,
    register_plugin_path,
    register_plugin,

    registered_host,
    registered_plugin_paths,
    registered_root,

    deregister_plugin,
    deregister_plugin_path,
)

from .lib import (
    time,
    logger,
)


__all__ = [
    "install",
    "uninstall",

    "schema",

    "Loader",
    "Creator",
    "discover",
    "Session",
    "session",

    "on",
    "after",
    "before",
    "emit",

    "publish",
    "create",
    "load",
    "update",
    "remove",

    "update_current_context",
    "get_representation_path",
    "loaders_from_representation",

    "register_host",
    "register_plugin_path",
    "register_plugin",
    "register_root",

    "registered_root",
    "registered_plugin_paths",
    "registered_host",

    "deregister_plugin",
    "deregister_plugin_path",

    "logger",
    "time",
]
