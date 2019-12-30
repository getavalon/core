"""Public API

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .pipeline import (
    install,
    uninstall,
    Creator,
    Loader,
    ls,
    publish,
    containerise,
)

from .workio import (
    open_file,
    save_file,
    current_file,
    has_unsaved_changes,
    file_extensions,
    work_root,
)

from .lib import (
    lsattr,
    lsattrs,
    read,
    maintained_selection,
    get_selection,
    # unique_name,
)


__all__ = [
    "install",
    "uninstall",
    "Creator",
    "Loader",
    "ls",
    "publish",
    "containerise",

    # Workfiles API
    "open_file",
    "save_file",
    "current_file",
    "has_unsaved_changes",
    "file_extensions",
    "work_root",

    # Utility functions
    "maintained_selection",
    "lsattr",
    "lsattrs",
    "read",
    "get_selection",
    # "unique_name",
]
