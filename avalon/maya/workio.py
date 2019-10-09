"""Host API required Work Files tool"""
import os

from maya import cmds


def file_extensions():
    return [".ma", ".mb"]


def has_unsaved_changes():
    return cmds.file(query=True, modified=True)


def save_file(filepath):
    cmds.file(rename=filepath)
    cmds.file(save=True, type="mayaAscii")


def open_file(filepath):
    return cmds.file(filepath, open=True, force=True)


def current_file():

    current_filepath = cmds.file(query=True, sceneName=True)
    if not current_filepath:
        return None

    return current_filepath


def work_root():

    # Base the root on the current Maya workspace.
    return os.path.join(
        cmds.workspace(query=True, rootDirectory=True),
        cmds.workspace(fileRuleEntry="scene")
    )
