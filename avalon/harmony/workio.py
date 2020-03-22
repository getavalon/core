"""Host API required Work Files tool"""
import os
import shutil
import zipfile
import signal

from . import lib


def _get_temp_path(filepath):
    basename = os.path.splitext(os.path.basename(filepath))[0]
    harmony_path = os.path.join(os.path.expanduser("~"), ".avalon", "harmony")
    return os.path.join(harmony_path, basename)


def file_extensions():
    return [".zip"]


def has_unsaved_changes():
    return lib.server.send({"function": "scene.isDirty"})["result"]


def save_file(filepath):
    temp_path = _get_temp_path(filepath)

    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)

    lib.server.send(
        {"function": "scene.saveAs", "args": [temp_path]}
    )["result"]

    lib.zip_and_move(temp_path, filepath)


def open_file(filepath):
    temp_path = _get_temp_path(filepath)

    with zipfile.ZipFile(filepath, "r") as zip_ref:
        zip_ref.extractall(temp_path)

    # Close existing scene.
    os.kill(lib.pid, signal.SIGTERM)

    # Stop server.
    lib.server.stop()

    # Save workfile path for later.
    lib.workfile_path = filepath

    # Launch new scene.
    scene_path = os.path.join(
        temp_path, os.path.basename(temp_path) + ".xstage"
    )
    lib.launch(lib.application_path, scene_path=scene_path)


def current_file():
    """Returning None to make Workfiles app look at first file extension."""
    return None


def work_root(session):
    return os.path.normpath(session["AVALON_WORKDIR"]).replace("\\", "/")
