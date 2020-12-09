"""Public API

Anything that isn't defined here is INTERNAL and unreliable for external use.

"""

from .pipeline import (
    install,
    ls
)

from .lib import (
    launch
)

from .workio import (
    save_file
)

from ..toonboom import (
    open_file,
    current_file,
    has_unsaved_changes,
    file_extensions,
    work_root
)

__all__ = [
    # Pipeline API.
    "install",
    "ls",

    # Library API.
    "launch",

    # Workfiles API.
    "save_file",
    "open_file",
    "current_file",
    "has_unsaved_changes",
    "file_extensions",
    "work_root"
]
