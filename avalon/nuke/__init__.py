"""Public API

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .lib import (
    add_publish_knob,
    ls_img_sequence,
    maintained_selection,
    get_node_path,
    get_avalon_knob_data,
    set_avalon_knob_data,
    imprint,
    find_copies,
    sync_copies
)

from .workio import (
    file_extensions,
    has_unsaved_changes,
    save_file,
    open_file,
    current_file,
    work_root,
)

from .pipeline import (
    install,
    uninstall,
    ls,
    publish,
    Creator,
    containerise,
    parse_container,
    update_container,
    get_handles,
    viewer_update_and_undo_stop,
    reload_pipeline,
)

__all__ = [
    # Lib API.
    "add_publish_knob",
    "ls_img_sequence",
    "maintained_selection",
    "get_node_path",
    "get_avalon_knob_data",
    "set_avalon_knob_data",
    "imprint",
    "find_copies",
    "sync_copies",

    # Workfiles API
    "file_extensions",
    "has_unsaved_changes",
    "save_file",
    "open_file",
    "current_file",
    "work_root",

    # Pipeline API.
    "install",
    "uninstall",
    "ls",
    "publish",
    "Creator",
    "containerise",
    "parse_container",
    "update_container",
    "get_handles",

    # Experimental
    "viewer_update_and_undo_stop",
    "reload_pipeline"
]

# Backwards API compatibility
open = open_file
save = save_file
