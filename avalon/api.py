"""Public application programming interface

The following members are public and reliable.
That is to say, anything **not** defined here is **internal**
and likely **unreliable** for use outside of the codebase itself.

|
|

"""

from . import schema
from . mongodb import (
    AvalonMongoDB,
    session_data_from_environment
)
from .pipeline import (
    install,
    uninstall,

    CreatorError,

    Loader,
    Creator,
    Action,
    InventoryAction,
    Application,
    discover,
    Session,

    # Deprecated
    Session as session,

    on,
    after,
    before,
    emit,

    publish,
    create,
    load,
    update,
    switch,
    remove,

    data,

    update_current_task,
    get_representation_path,
    loaders_from_representation,

    register_root,
    register_host,
    register_plugin_path,
    register_plugin,

    registered_host,
    registered_config,
    registered_plugin_paths,
    registered_root,

    deregister_plugin,
    deregister_plugin_path,

    HOST_WORKFILE_EXTENSIONS,
    format_template_with_optional_keys,
    last_workfile_with_version,
    last_workfile
)

from .lib import (
    time,
    logger,
)


__all__ = [
    "AvalonMongoDB",
    "session_data_from_environment",

    "install",
    "uninstall",

    "schema",

    "CreatorError",

    "Loader",
    "Creator",
    "Action",
    "InventoryAction",
    "Application",
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
    "switch",
    "remove",

    "data",

    "update_current_task",
    "get_representation_path",
    "loaders_from_representation",

    "register_host",
    "register_plugin_path",
    "register_plugin",
    "register_root",

    "registered_root",
    "registered_plugin_paths",
    "registered_host",
    "registered_config",

    "deregister_plugin",
    "deregister_plugin_path",

    "HOST_WORKFILE_EXTENSIONS",
    "should_start_last_workfile",
    "format_template_with_optional_keys",
    "last_workfile_with_version",
    "last_workfile",

    "logger",
    "time",
]
