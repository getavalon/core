"""A wrapper for the `bpy` module.

This a a 'quick hack' to remedy an issue with running Qt apps inside of Blender.
The problem is that `bpy.context` is not fully populated when queried from inside a Qt app.
In the future the underlying problem should definitely be fixed, but for now
this is a fairly simple workaround. The only thing that needs to be changed in
other modules and plug-ins is the import statement. These should be changed to
`from avalon.blender import bpy` (instead of `import bpy`).

So far it seems everything is fine on Linux, on Windows `bpy.context` contains
almost nothing, hence this 'fix'. On macOS the situation is worse: both Blender
and the Qt app interfaces are basically locked when starting the Qt app.
"""

from typing import Dict, List, Optional

import bpy as _bpy


class BpyContext:
    """Because there are issues with retreiving `bpy.context` from a Qt app
    (for example 'selected_objects'), you can use this class instead. It tries
    to fill in all missing keys.

    This object should behave (almost) identical to the regular `bpy.context`
    object.

    The process is simple:
    If an attribute is found in the original `bpy.context` simply return it. If
    it is not found try to determine the proper value in another way.

    Note:
        To add more overrides, simply add the relevant properties and functions.
        Also add them to the `copy` method, else they will not be available
        when you do a `bpy.context.copy()`.
    """

    def __getattr__(self, name):
        return getattr(_bpy.context, name)

    def __setattr__(self, name, value):
        setattr(_bpy.context, name, value)

    @property
    def active_object(self):
        return self._active_object()

    @property
    def object(self):
        return self._active_object()

    @property
    def selected_objects(self):
        return self._selected_objects()

    def copy(self) -> Dict:
        """Mimic `bpy.context.copy()`.

        Return `bpy.context.copy()` with the missing keys added.
        """

        copy = _bpy.context.copy()
        copy['active_object'] = copy.get(
            'active_object',
            self._active_object(),
        )
        copy['object'] = copy.get(
            'object',
            self._active_object(),
        )
        copy['selected_objects'] = copy.get(
            'selected_objects',
            self._selected_objects(),
        )

        return copy

    def _active_object(self) -> Optional[_bpy.types.Object]:
        """Return the active object from the view layer."""

        return _bpy.context.view_layer.objects.active

    def _selected_objects(self) -> List[Optional[_bpy.types.Object]]:
        """Return the selected objects from the view layer."""

        return [obj for obj in _bpy.context.scene.objects if obj.select_get()]


context = BpyContext()


def __getattr__(name):
    """Return the attribute from `bpy` if it is not defined here."""
    return getattr(_bpy, name)
