"""Host API required Work Files tool"""
import os
from . import lib


def _is_document_open():
    if lib.send_extendscript("app.documents.length"):
        return True

    return False


def file_extensions():
    return [".psd"]


def has_unsaved_changes():
    if _is_document_open():
        return not lib.send_extendscript("app.activeDocument.saved")

    return False


def save_file(filepath):
    lib.send_extendscript("app.activeDocument.SaveAs(\"{}\")".format(filepath))


def open_file(filepath):
    lib.send_extendscript(
        "var fileRef = new File(\"{}\");app.open(fileRef);".format(
            filepath.replace("\\", "/")
        )
    )
    return True


def current_file():
    if _is_document_open():
        current_file = lib.send_extendscript("app.activeDocument.fullName")
        return os.path.normpath(current_file).replace("\\", "/")


def work_root():
    from avalon import Session
    return os.path.normpath(Session["AVALON_WORKDIR"]).replace("\\", "/")
