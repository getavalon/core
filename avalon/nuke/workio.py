"""Host API required Work Files tool"""
import os
import nuke


def file_extensions():
    return [".nk"]


def has_unsaved_changes():
    return nuke.root().modified()


def save(filepath):
    path = filepath.replace("\\", "/")
    nuke.scriptSaveAs(path)


def open(filepath):
    if nuke.Root().modified():
        result = self.save_changes_prompt()

        if result is None:
            return False
        if result:
            nuke.scriptSave()

    # To remain in the same window, we have to clear the script and read
    # in the contents of the workfile.
    nuke.scriptClear()
    nuke.scriptReadFile(file_path)
    nuke.Root()["name"].setValue(file_path)
    nuke.Root()["project_directory"].setValue(os.path.dirname(file_path))
    nuke.Root().setModified(False)

    return True


def current_file():
    current_file = nuke.root().name()

    # Unsaved current file
    if current_file == 'Root':
        return None

    return os.path.normpath(current_file)


def work_root():

    from avalon import api

    return os.path.normpath(api.Session["AVALON_WORKDIR"])
