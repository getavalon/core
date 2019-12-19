"""Blender operators and menus for use with Avalon."""

import os
import sys
from distutils.util import strtobool
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, Union

import bpy
import bpy.utils.previews

from .. import api
from ..vendor.Qt import QtWidgets


preview_collections: Dict = dict()


def _is_avalon_in_debug_mode() -> bool:
    """Check if Avalon is in debug mode."""

    try:
        # It says `strtobool` returns a bool, but it returns an int :/
        return bool(strtobool(os.environ.get('AVALON_DEBUG', "False")))
    except (ValueError, AttributeError):
        # If it can't logically be converted to a bool, assume it's False.
        return False


class LaunchQtApp(bpy.types.Operator):
    """A Base class for opertors to launch a Qt app."""

    _app: Optional[QtWidgets.QApplication]
    _window: Optional[Union[QtWidgets.QDialog, ModuleType]]
    _timer: Optional[bpy.types.Timer]
    _show_args: Optional[List]
    _show_kwargs: Optional[Dict]

    def __init__(self):
        print(f"Initialising {self.bl_idname}...")
        app_instance = QtWidgets.QApplication.instance()
        if not app_instance:
            from .. import style
            app_instance = QtWidgets.QApplication(sys.argv)
            app_instance.setStyleSheet(style.load_stylesheet())

        self._app = app_instance

    def _is_window_visible(self) -> bool:
        """Check if the window of the app is visible.

        If `self._window` is an instance of `QtWidgets.QDialog`, simply return
        `self._window.isVisible()`. If `self._window` is a module check
        if it has `self._window.app.window` and if so, return `isVisible()`
        on that.
        Else return False, because we don't know how to check if the
        window is visible.
        """

        window: Optional[QtWidgets.QDialog] = None
        if isinstance(self._window, QtWidgets.QDialog):
            window = self._window
        if isinstance(self._window, ModuleType):
            try:
                window = self._window.app.window
            except AttributeError:
                return False

        try:
            return window is not None and window.isVisible()
        except (AttributeError, RuntimeError):
            pass

        return False

    def modal(self, context, event):
        """Run modal to keep Blender and the Qt UI responsive."""
        if event.type == 'TIMER':
            if self._is_window_visible():
                # Process events if the window is visible
                self._app.processEvents()
            else:
                # Stop the operator if the window is closed
                self.cancel(context)
                print(f"Stopping modal execution of '{self.bl_idname}'")
                return {'FINISHED'}

        return {'PASS_THROUGH'}

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
        if getattr(self, "_window") is None:
            raise AttributeError("`self._window` should be set.")
        if not isinstance(self._window, (QtWidgets.QDialog, ModuleType)):
            raise AttributeError(
                "`self._window` should be a `QDialog or module`.")

        args = getattr(self, "_show_args", list())
        kwargs = getattr(self, "_show_kwargs", dict())
        self._window.show(*args, **kwargs)

        self._timer = context.window_manager.event_timer_add(
            1/120, window=context.window
        )
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        """Remove the event timer when stopping the operator."""
        context.window_manager.event_timer_remove(self._timer)


class LaunchContextManager(LaunchQtApp):
    """Launch Avalon Context Manager."""

    bl_idname = "wm.avalon_contextmanager"
    bl_label = "Set Avalon Context..."

    def execute(self, context):
        from ..tools import contextmanager
        self._window = contextmanager
        return super().execute(context)


class LaunchCreator(LaunchQtApp):
    """Launch Avalon Creator."""

    bl_idname = "wm.avalon_creator"
    bl_label = "Create..."

    def execute(self, context):
        from ..tools import creator
        self._window = creator
        # self._show_kwargs = {'debug': _is_avalon_in_debug_mode()}
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
            # 'debug': _is_avalon_in_debug_mode(),
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
        # self._show_kwargs = {'debug': _is_avalon_in_debug_mode()}
        return super().execute(context)


class LaunchWorkFiles(LaunchQtApp):
    """Launch Avalon Work Files."""

    bl_idname = "wm.avalon_workfiles"
    bl_label = "Work Files..."

    def execute(self, context):
        from ..tools import workfiles
        root = str(Path(os.environ.get("AVALON_WORKDIR", ""), "scene"))
        self._window = workfiles
        self._show_kwargs = {"root": root}
        return super().execute(context)


class LaunchTestApp(LaunchQtApp):
    """Launch a simple test app."""

    bl_idname = "wm.avalon_test_app"
    bl_label = "Test App..."

    def execute(self, context):
        from .. import style
        self._window = TestApp()
        self._window.setStyleSheet(style.load_stylesheet())
        return super().execute(context)


class TOPBAR_MT_avalon(bpy.types.Menu):
    """Avalon menu."""

    bl_idname = "TOPBAR_MT_avalon"
    bl_label = "Avalon"

    def draw(self, context):
        """Draw the menu in the UI."""

        layout = self.layout

        pcoll = preview_collections.get("avalon")
        if pcoll:
            pyblish_menu_icon = pcoll["pyblish_menu_icon"]
            pyblish_menu_icon_id = pyblish_menu_icon.icon_id
        else:
            pyblish_menu_icon_id = 0

        asset = api.Session['AVALON_ASSET']
        task = api.Session['AVALON_TASK']
        context_label = f"{asset}, {task}"
        layout.operator(LaunchContextManager.bl_idname, text=context_label)
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
        if _is_avalon_in_debug_mode():
            layout.separator()
            layout.operator(LaunchTestApp.bl_idname, text="Test App...")
        # TODO (jasper): maybe add 'Reload Pipeline', 'Reset Frame Range' and
        #                'Reset Resolution'?


def draw_avalon_menu(self, context):
    """Draw the Avalon menu in the top bar."""

    self.layout.menu(TOPBAR_MT_avalon.bl_idname)


classes = [
    LaunchContextManager,
    LaunchCreator,
    LaunchLoader,
    LaunchPublisher,
    LaunchManager,
    LaunchWorkFiles,
]
if _is_avalon_in_debug_mode():
    # Enable the test app in debug mode
    classes.append(LaunchTestApp)
classes.append(TOPBAR_MT_avalon)


def register():
    "Register the operators and menu."

    pcoll = bpy.utils.previews.new()
    pyblish_icon_file = Path(__file__).parent / "icons" / "pyblish-32x32.png"
    pcoll.load("pyblish_menu_icon", str(pyblish_icon_file.absolute()), 'IMAGE')
    preview_collections["avalon"] = pcoll

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_avalon_menu)


def unregister():
    """Unregister the operators and menu."""

    pcoll = preview_collections.pop("avalon")
    bpy.utils.previews.remove(pcoll)
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_avalon_menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
