import subprocess
import threading
import os
import random
import zipfile
import sys
import importlib
import queue

from .server import Server
from ..vendor.Qt import QtWidgets

self = sys.modules[__name__]
self.server = None
self.pid = None
self.application_path = None
self.callback_queue = None


def execute_in_main_thread(func_to_call_from_main_thread):
    self.callback_queue.put(func_to_call_from_main_thread)


def main_thread_listen():
    callback = self.callback_queue.get()
    callback()


def launch(application_path, scene_path=None):
    """Setup for Harmony launch.
    """
    from avalon import api, harmony

    api.install(harmony)

    port = random.randrange(5000, 6000)
    os.environ["AVALON_HARMONY_PORT"] = str(port)

    # Launch Harmony.
    os.environ["TOONBOOM_GLOBAL_SCRIPT_LOCATION"] = os.path.dirname(__file__)

    path = scene_path
    if not scene_path:
        harmony_path = os.path.join(
            os.path.expanduser("~"), ".avalon", "harmony"
        )
        zip_file = os.path.join(os.path.dirname(__file__), "temp_scene.zip")
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(harmony_path)

        path = os.path.join(harmony_path, "temp", "temp.xstage")

    process = subprocess.Popen([application_path, path])

    self.pid = process.pid
    self.application_path = application_path

    # Launch Avalon server.
    self.server = Server(port)
    thread = threading.Thread(target=self.server.start)
    thread.deamon = True
    thread.start()

    if not scene_path:
        self.callback_queue = queue.Queue()
        while True:
            main_thread_listen()


def show(module_name):
    """Call show on "module_name".

    This allows to make a QApplication ahead of time and always "exec_" to
    prevent crashing.

    Args:
        module_name (str): Name of module to call "show" on.
    """
    # Need to have an existing QApplication.
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    # Import and show tool.
    module = importlib.import_module(module_name)
    module.show()

    # QApplication needs to always execute.
    if "publish" in module_name:
        return

    app.exec_()
