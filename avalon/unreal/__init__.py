"""Public API

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .pipeline import (
    install,
    uninstall,
    Creator,
    Loader,
    ls,
    load,  # deprecated (old load api)
    create,  # deprecated (old creator api)
    remove,  # deprecated (old load api)
    update,  # deprecated (old load api)
    publish,
    containerise,
    lock,
    unlock,
    is_locked,
    lock_ignored,
)

from .workio import (
    open_file,
    save_file,
    current_file,
    has_unsaved_changes,
    file_extensions,
    work_root,
)

__all__ = [
    "install",
    "uninstall",
    "Creator",
    "Loader",
    "ls",
    "load",
    "create",
    "remove",
    "update",
    "publish",
    "lock",
    "unlock",
    "is_locked",
    "lock_ignored",
    # Workfiles API
    "open_file",
    "save_file",
    "current_file",
    "has_unsaved_changes",
    "file_extensions",
    "work_root",
]

# Backwards API compatibility
open = open_file
save = save_file
