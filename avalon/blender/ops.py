"""Blender operators and menus for use with Avalon."""

import os
import sys
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, Union

import bpy
import bpy.utils.previews

from ..tools.contextmanager.app import App as contextmanager_window
from ..tools.creator.app import Window as creator_window
from ..tools.loader.app import Window as loader_window
from ..tools.workfiles.app import Window as workfiles_window
from ..tools.sceneinventory.app import Window as sceneinventory_window
from ..tools import publish

from .. import api
from ..vendor.Qt import QtWidgets, QtCore

PREVIEW_COLLECTIONS: Dict = dict()

# This seems like a good value to keep the Qt app responsive and doesn't slow
# down Blender. At least on macOS I the interace of Blender gets very laggy if
# you make it smaller.
TIMER_INTERVAL: float = 0.01


class BlenderApplication(QtWidgets.QApplication):
    _instance = None
    blender_windows = {}

    def __init__(self, *args, **kwargs):
        super(BlenderApplication, self).__init__(*args, **kwargs)
        self.setQuitOnLastWindowClosed(False)

        from .. import style
        self.setStyleSheet(style.load_stylesheet())
        self.lastWindowClosed.connect(self.__class__.reset)

    @classmethod
    def get_app(cls):
        if cls._instance is None:
            cls._instance = cls(sys.argv)
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    @classmethod
    def store_window(cls, identifier, window):
        current_window = cls.get_window(identifier)
        cls.blender_windows[identifier] = window
        if current_window:
            current_window.close()
            # current_window.deleteLater()

    @classmethod
    def get_window(cls, identifier):
        return cls.blender_windows.get(identifier)


def _has_visible_windows(app: QtWidgets.QApplication) -> bool:
    """Check if the Qt application has any visible top level windows."""
    is_visible = False
    for window in BlenderApplication.blender_windows.values():
        try:
            if window.isVisible():
                is_visible = True
                break
        except RuntimeError:
            continue

    return False


def _process_app_events(app: QtWidgets.QApplication) -> Optional[float]:
    """Process the events of the Qt app if the window is still visible.

    If the app has any top level windows and at least one of them is visible
    return the time after which this function should be run again. Else return
    None, so the function is not run again and will be unregistered.
    """
    if app._instance and _has_visible_windows(app):
        app.processEvents()
        return TIMER_INTERVAL

    bpy.context.window_manager['is_avalon_qt_timer_running'] = False
    return None


class LaunchQtApp(bpy.types.Operator):
    """A Base class for opertors to launch a Qt app."""

    _app: QtWidgets.QApplication
    _window = Union[QtWidgets.QDialog, ModuleType]
    _window_class: QtWidgets.QDialog = None
    _init_args: Optional[List] = list()
    _init_kwargs: Optional[Dict] = dict()
    bl_idname: str = None

    def __init__(self):
        from .. import style
        if self.bl_idname is None:
            raise NotImplementedError("Attribute `bl_idname` must be set!")
        print(f"Initialising {self.bl_idname}...")
        self._app = BlenderApplication.get_app()

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

        if self._window_class is None:
            if self._window is None:
                raise AttributeError("`self._window` is not set.")

        else:
            window = self._app.get_window(self.bl_idname)
            if window is None:
                window = self._window_class(
                    *self._init_args, **self._init_kwargs
                )
                self._app.store_window(self.bl_idname, window)
            self._window = window

        if not isinstance(self._window, (QtWidgets.QDialog, ModuleType)):
            raise AttributeError(
                "`window` should be a `QDialog or module`. Got: {}".format(
                    str(type(window))
                )
            )

        self.before_window_show()

        if isinstance(self._window, ModuleType):
            self._window.show()
            window = None
            if hasattr(self._window, "window"):
                window = self._window.window
            elif hasattr(self._window, "_window"):
                window = self._window.window

            if window:
                self._app.store_window(self.bl_idname, window)

        else:
            origin_flags = self._window.windowFlags()
            on_top_flags = origin_flags | QtCore.Qt.WindowStaysOnTopHint
            self._window.setWindowFlags(on_top_flags)
            self._window.show()

            if on_top_flags != origin_flags:
                self._window.setWindowFlags(origin_flags)
                self._window.show()

        wm = bpy.context.window_manager
        if not wm.get('is_avalon_qt_timer_running', False):
            bpy.app.timers.register(
                partial(_process_app_events, self._app),
                persistent=True,
            )
            wm['is_avalon_qt_timer_running'] = True

        return {'FINISHED'}

    def before_window_show(self):
        return


        wm = bpy.context.window_manager
        if not wm.get('is_avalon_qt_timer_running', False):
            bpy.app.timers.register(
                partial(_process_app_events, self._app),
                persistent=True,
            )
            wm['is_avalon_qt_timer_running'] = True

    bl_idname = "wm.avalon_contextmanager"
    bl_label = "Set Avalon Context..."
    _window_class = contextmanager_window


class LaunchCreator(LaunchQtApp):
    """Launch Avalon Creator."""

    bl_idname = "wm.avalon_creator"
    bl_label = "Create..."
    _window_class = creator_window

    def before_window_show(self):
        self._window.refresh()


class LaunchLoader(LaunchQtApp):
    """Launch Avalon Loader."""

    bl_idname = "wm.avalon_loader"
    bl_label = "Load..."
    _window_class = loader_window

    def before_window_show(self):
        self._window.set_context(
            {"asset": api.Session["AVALON_ASSET"]},
            refresh=True
        )


class LaunchPublisher(LaunchQtApp):
    """Launch Avalon Publisher."""

    bl_idname = "wm.avalon_publisher"
    bl_label = "Publish..."

    def execute(self, context):
        publish_show = publish._discover_gui()
        publish.show()
        return {'FINISHED'}


class LaunchManager(LaunchQtApp):
    """Launch Avalon Manager."""

    bl_idname = "wm.avalon_manager"
    bl_label = "Manage..."
    _window_class = sceneinventory_window

    def before_window_show(self):
        self._window.refresh()


class LaunchWorkFiles(LaunchQtApp):
    """Launch Avalon Work Files."""

    bl_idname = "wm.avalon_workfiles"
    bl_label = "Work Files..."
    _window_class = workfiles_window

    def execute(self, context):
        self._init_kwargs = {
            "root": str(Path(
                os.environ.get("AVALON_WORKDIR", ""),
                os.environ.get("AVALON_SCENEDIR", ""),
            ))
        }
        return super().execute(context)

    def before_window_show(self):
        self._window.root = str(Path(
            os.environ.get("AVALON_WORKDIR", ""),
            os.environ.get("AVALON_SCENEDIR", ""),
        ))
        self._window.refresh()


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
