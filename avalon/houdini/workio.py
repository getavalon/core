"""Host API required Work Files tool"""
import os

import hou


def file_extensions():
    return [".hip", ".hiplc", ".hipnc"]


def has_unsaved_changes():
    return hou.hipFile.hasUnsavedChanges()


def save(filepath):

    # Force forwards slashes to avoid segfault
    filepath = filepath.replace("\\", "/")

    hou.hipFile.save(file_name=filepath,
                     save_to_recent_files=True)

    return filepath


def open(filepath):

    # Force forwards slashes to avoid segfault
    filepath = filepath.replace("\\", "/")

    hou.hipFile.load(filepath,
                     suppress_save_prompt=True,
                     ignore_load_warnings=False)

    return filepath


def current_file():

    current_filepath = hou.hipFile.path()
    if (os.path.basename(current_filepath) == "untitled.hip" and
            not os.path.exists(current_filepath)):
        # By default a new scene in houdini is saved in the current
        # working directory as "untitled.hip" so we need to capture
        # that and consider it 'not saved' when it's in that state.
        return None

    return current_filepath


def work_root():
    from .. import api
    return os.path.join(api.Session["AVALON_WORKDIR"], "scenes")
