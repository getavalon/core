"""Public API

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .pipeline import (
    ls,
    Creator,
    install,
    containerise
)

from .workio import (
    file_extensions,
    has_unsaved_changes,
    save_file,
    open_file,
    current_file,
    work_root,
)

from .lib import (
    start_server,
    app,
    maintained_selection,
    maintained_visibility,
    get_layers_in_document,
    get_layers_in_layers,
    read,
    com_objects,
    import_as_smart_object
)

__all__ = [
    # pipeline
    "ls",
    "Creator",
    "install",
    "containerise",

    # workfiles
    "file_extensions",
    "has_unsaved_changes",
    "save_file",
    "open_file",
    "current_file",
    "work_root",

    # lib
    "start_server",
    "app",
    "maintained_selection",
    "maintained_visibility",
    "get_layers_in_document",
    "get_layers_in_layers",
    "read",
    "com_objects",
    "import_as_smart_object"
]
