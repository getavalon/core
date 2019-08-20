"""Host API required by Work Files tool"""
import os
import nuke


def file_extensions():
    return [".nk"]


def has_unsaved_changes():
    return nuke.Root().modified()


def save(filepath):
    nuke.scriptSaveAs(filepath)


def open(filepath):
    nuke.scriptClear()
    nuke.scriptOpen(filepath)
    return True


def current_file():
    current_file = nuke.root().name()
    normalised = os.path.normpath(current_file)

    # Unsaved current file
    if nuke.Root().name() == 'Root':
        return "NOT SAVED"

    return normalised


def work_root():
    from avalon import Session

    work_dir = Session["AVALON_WORKDIR"]
    scene_dir = Session.get("AVALON_SCENEDIR")

    if scene_dir:
        return os.path.join(work_dir, scene_dir)
    else:
        return work_dir
