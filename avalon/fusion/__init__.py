"""Public API

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .pipeline import (
    install,

    ls,

    imprint_container,
    parse_container,

    get_current_comp,
    comp_lock_and_undo_chunk

)

from .workio import (
    open_file,
    save_file,
    current_file,
    has_unsaved_changes,
    file_extensions,
    work_root
)

from .lib import (
    maintained_selection
)

__all__ = [
    "install",

    "ls",

    "imprint_container",
    "parse_container",

    "get_current_comp",
    "comp_lock_and_undo_chunk",

    # Workfiles API
    "open_file",
    "save_file",
    "current_file",
    "has_unsaved_changes",
    "file_extensions",
    "work_root",

    "maintained_selection"

]

# Backwards API compatibility
open = open_file
save = save_file
