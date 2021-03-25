"""Public API

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .pipeline import (
    ls,
    install,
    Creator,
    containerise
)

from .lib import (
    launch,
    maintained_selection,
    imprint,
    read,
    send,
    maintained_nodes_state,
    save_scene,
    save_scene_as,
    remove,
    find_node_by_name,
    signature
)

from .workio import (
    open_file,
    save_file,
    current_file,
    has_unsaved_changes,
    file_extensions,
    work_root
)

__all__ = [
    # pipeline
    "ls",
    "install",
    "Creator",
    "containerise",

    # lib
    "launch",
    "maintained_selection",
    "imprint",
    "read",
    "send",
    "maintained_nodes_state",
    "save_scene",
    "save_scene_as",
    "remove",
    "find_node_by_name",
    "signature",

    # Workfiles API
    "open_file",
    "save_file",
    "current_file",
    "has_unsaved_changes",
    "file_extensions",
    "work_root",
]
