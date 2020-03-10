"""Host API required Work Files tool"""
import os

from . import lib


def file_extensions():
    return [".zip", ".xstage"]


def has_unsaved_changes():
    pass


def save_file(filepath):
    pass


def open_file(filepath):
    pass


def current_file():
    pass


def work_root(session):
    return os.path.normpath(session["AVALON_WORKDIR"]).replace("\\", "/")
