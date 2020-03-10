import subprocess
import threading
import os
import random
import zipfile
import sys

from .server import Server

self = sys.modules[__name__]
self.server = None


def launch(application):
    """Setup for Harmony launch.
    """
    from avalon import api, harmony

    api.install(harmony)

    # Launch Avalon server.
    os.environ["AVALON_QTAPPLICATION_EXEC"] = str(True)
    port = random.randrange(5000, 6000)
    os.environ["AVALON_HARMONY_PORT"] = str(port)

    self.server = Server(port)
    thread = threading.Thread(target=self.server.start)
    thread.deamon = True
    thread.start()

    # Launch Harmony.
    os.environ["TOONBOOM_GLOBAL_SCRIPT_LOCATION"] = os.path.dirname(__file__)

    harmony_path = os.path.join(
        os.path.expanduser("~"), ".avalon", "harmony"
    )
    zip_file = os.path.join(os.path.dirname(__file__), "temp_scene.zip")
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(harmony_path)

    subprocess.Popen(
        [application, os.path.join(harmony_path, "temp", "temp.xstage")]
    )
