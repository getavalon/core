"""Host API required Work Files tool"""
import os

from . import lib


def _active_document():
    if len(lib.app.Documents) < 1:
        return None

    return lib.app.ActiveDocument


def file_extensions():
    return [".psd"]


def has_unsaved_changes():
    if _active_document():
        return not _active_document().Saved

    return False


def save_file(filepath):
    _active_document().SaveAs(filepath)


def open_file(filepath):
    lib.app.Open(filepath)

    return True


def current_file():
    if _active_document():
        return os.path.normpath(_active_document().FullName).replace("\\", "/")


def work_root():
    from avalon import Session
    return os.path.normpath(Session["AVALON_WORKDIR"]).replace("\\", "/")
