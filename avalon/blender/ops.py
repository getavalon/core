"""Blender operators and menus for use with Avalon."""

import os
import sys
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, Union

import bpy
import bpy.utils.previews

from .. import api
from ..vendor.Qt import QtWidgets

PREVIEW_COLLECTIONS: Dict = dict()

# This seems like a good value to keep the Qt app responsive and doesn't slow
# down Blender. At least on macOS I the interace of Blender gets very laggy if
# you make it smaller.
TIMER_INTERVAL: float = 0.01


def _has_visible_windows(app: QtWidgets.QApplication) -> bool:
    """Check if the Qt application has any visible top level windows."""

    for window in app.topLevelWindows():
        try:
            if window.isVisible():
                return True
        except RuntimeError:
            continue

    return False


def _process_app_events(app: QtWidgets.QApplication) -> Optional[float]:
    """Process the events of the Qt app if the window is still visible.

    If the app has any top level windows and at least one of them is visible
    return the time after which this function should be run again. Else return
    None, so the function is not run again and will be unregistered.
    """

    if _has_visible_windows(app):
        app.processEvents()
        return TIMER_INTERVAL

    bpy.context.window_manager['is_avalon_qt_timer_running'] = False
    return None


class LaunchQtApp(bpy.types.Operator):
    """A Base class for opertors to launch a Qt app."""

    _app: QtWidgets.QApplication
    _window: Union[QtWidgets.QDialog, ModuleType]
    _show_args: Optional[List]
    _show_kwargs: Optional[Dict]

    def __init__(self):
        from .. import style
        print(f"Initialising {self.bl_idname}...")
        self._app = (QtWidgets.QApplication.instance()
                     or QtWidgets.QApplication(sys.argv))
        self._app.setStyleSheet(style.load_stylesheet())

    def execute(self, context):
        """Execute the operator.

        The child class must implement `execute()` where it only has to set
        `self._window` to the desired Qt window and then simply run
        `return super().execute(context)`.
        `self._window` is expected to have a `show` method.
        If the `show` method requires arguments, you can set `self._show_args`
        and `self._show_kwargs`. `args` should be a list, `kwargs` a
        dictionary.
        """

        # Check if `self._window` is properly set
        if getattr(self, "_window", None) is None:
            raise AttributeError("`self._window` should be set.")
        if not isinstance(self._window, (QtWidgets.QDialog, ModuleType)):
            raise AttributeError(
                "`self._window` should be a `QDialog or module`.")

        args = getattr(self, "_show_args", list())
        kwargs = getattr(self, "_show_kwargs", dict())
        self._window.show(*args, **kwargs)

        wm = bpy.context.window_manager
        if not wm.get('is_avalon_qt_timer_running', False):
            bpy.app.timers.register(
                partial(_process_app_events, self._app),
                persistent=True,
            )
            wm['is_avalon_qt_timer_running'] = True

        return {'FINISHED'}


class LaunchCreator(LaunchQtApp):
    """Launch Avalon Creator."""

    bl_idname = "wm.avalon_creator"
    bl_label = "Create..."

    def execute(self, context):
        from ..tools import creator
        self._window = creator
        return super().execute(context)


class LaunchLoader(LaunchQtApp):
    """Launch Avalon Loader."""

    bl_idname = "wm.avalon_loader"
    bl_label = "Load..."

    def execute(self, context):
        from ..tools import loader
        self._window = loader
        if self._window.app.window is not None:
            self._window.app.window = None
        self._show_kwargs = {
            'use_context': True,
        }
        return super().execute(context)


class LaunchPublisher(LaunchQtApp):
    """Launch Avalon Publisher."""

    bl_idname = "wm.avalon_publisher"
    bl_label = "Publish..."

    def execute(self, context):
        from ..tools import publish
        publish_show = publish._discover_gui()
        if publish_show.__module__ == 'pyblish_qml':
            # When using Pyblish QML we don't have to do anything special
            publish.show()
            return {'FINISHED'}
        self._window = publish
        return super().execute(context)


class LaunchManager(LaunchQtApp):
    """Launch Avalon Manager."""

    bl_idname = "wm.avalon_manager"
    bl_label = "Manage..."

    def execute(self, context):
        from ..tools import cbsceneinventory
        self._window = cbsceneinventory
        return super().execute(context)


class LaunchWorkFiles(LaunchQtApp):
    """Launch Avalon Work Files."""

    bl_idname = "wm.avalon_workfiles"
    bl_label = "Work Files..."

    def execute(self, context):
        from ..tools import workfiles
        root = str(Path(
            os.environ.get("AVALON_WORKDIR", ""),
            os.environ.get("AVALON_SCENEDIR", "")
        ))
        self._window = workfiles
        self._show_kwargs = {"root": root}
        return super().execute(context)


class TOPBAR_MT_avalon(bpy.types.Menu):
    """Avalon menu."""

    bl_idname = "TOPBAR_MT_avalon"
    bl_label = "Avalon"

    def draw(self, context):
        """Draw the menu in the UI."""

        layout = self.layout

        pcoll = PREVIEW_COLLECTIONS.get("avalon")
        if pcoll:
            pyblish_menu_icon = pcoll["pyblish_menu_icon"]
            pyblish_menu_icon_id = pyblish_menu_icon.icon_id
        else:
            pyblish_menu_icon_id = 0

        asset = api.Session['AVALON_ASSET']
        task = api.Session['AVALON_TASK']
        context_label = f"{asset}, {task}"
        context_label_item = layout.row()
        context_label_item.operator(
            LaunchWorkFiles.bl_idname, text=context_label
        )
        context_label_item.enabled = False
        layout.separator()
        layout.operator(LaunchCreator.bl_idname, text="Create...")
        layout.operator(LaunchLoader.bl_idname, text="Load...")
        layout.operator(
            LaunchPublisher.bl_idname,
            text="Publish...",
            icon_value=pyblish_menu_icon_id,
        )
        layout.operator(LaunchManager.bl_idname, text="Manage...")
        layout.separator()
        layout.operator(LaunchWorkFiles.bl_idname, text="Work Files...")
        # TODO (jasper): maybe add 'Reload Pipeline', 'Reset Frame Range' and
        #                'Reset Resolution'?


def draw_avalon_menu(self, context):
    """Draw the Avalon menu in the top bar."""

    self.layout.menu(TOPBAR_MT_avalon.bl_idname)


classes = [
    LaunchCreator,
    LaunchLoader,
    LaunchPublisher,
    LaunchManager,
    LaunchWorkFiles,
    TOPBAR_MT_avalon,
]


def register():
    "Register the operators and menu."

    pcoll = bpy.utils.previews.new()
    pyblish_icon_file = Path(__file__).parent / "icons" / "pyblish-32x32.png"
    pcoll.load("pyblish_menu_icon", str(pyblish_icon_file.absolute()), 'IMAGE')
    PREVIEW_COLLECTIONS["avalon"] = pcoll

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_avalon_menu)


def unregister():
    """Unregister the operators and menu."""

    pcoll = PREVIEW_COLLECTIONS.pop("avalon")
    bpy.utils.previews.remove(pcoll)
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_avalon_menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
