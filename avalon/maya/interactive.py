"""Interactive functionality

These depend on user selection in Maya, and may be used as-is. They
implement the functionality in :mod:`commands.py`.

Each of these functions take `*args` as argument, because when used
in a Maya menu an additional argument is passed with metadata about
what state the button was pressed in. None of this data is used here.

"""

from . import commands


def reset_frame_range(*args):
    """Set frame range to current asset"""
    return commands.reset_frame_range()


def reset_resolution(*args):
    """Set frame range to current asset"""
    return commands.reset_resolution()
