import os
import sys


class Host(object):
    """The base class for a host.

    This sets forth the methods required for Work Files to work in any
    host and will have to be implemented per host.

    """

    @staticmethod
    def compatible():
        """Return whether the current running process is this Host."""
        return False

    def extensions(self):
        """Return the filename extension formats that should be shown.

        Note:
            The first entry in the list will be used as the default file
            format to save to when the current scene is not saved yet.

        Returns:
            list: A list of the file extensions supported by Work Files.

        """
        return list()

    def has_unsaved_changes(self):
        """Return whether current file has unsaved modifications."""

    def save(self, filepath):
        """Save to filepath"""
        pass

    def open(self, filepath):
        """Open file"""
        pass

    def current_file(self):
        """Return path to currently open file or None if not saved.

        Returns:
            str or None: The full path to current file or None.

        """
        pass

    def root(self):
        """Return the default root for the Host to browse in for Work Files

        Returns:
            str: The path to look in.

        """
        pass


class MayaHost(Host):
    """Maya host integration"""

    @staticmethod
    def compatible():
        basename = os.path.basename(sys.executable).lower()
        if "maya" in basename:
            return True

    def extensions(self):
        return [".ma", ".mb"]

    def has_unsaved_changes(self):
        from maya import cmds
        return cmds.file(query=True, modified=True)

    def save(self, filepath):
        from maya import cmds
        cmds.file(rename=filepath)
        cmds.file(save=True, type="mayaAscii")

    def open(self, filepath):
        from maya import cmds
        return cmds.file(filepath, open=True, force=True)

    def current_file(self):
        from maya import cmds

        current_file = cmds.file(query=True, sceneName=True)

        # Maya returns forward-slashes by default
        normalised = os.path.basename(os.path.normpath(current_file))

        # Unsaved current file
        if normalised == ".":
            return None

        return normalised

    def root(self):
        from maya import cmds

        # Base the root on the current Maya workspace.
        return os.path.join(
            cmds.workspace(query=True, rootDirectory=True),
            cmds.workspace(fileRuleEntry="scene")
        )


class FusionHost(Host):
    """Blackmagic Design Fusion host integration"""

    @staticmethod
    def compatible():
        basename = os.path.basename(sys.executable).lower()
        if "fusion" in basename or "fuscript" in basename:
            return True

    def extensions(self):
        return [".comp"]

    def has_unsaved_changes(self):
        from avalon.fusion.pipeline import get_current_comp

        comp = get_current_comp()
        return comp.GetAttrs()["COMPB_Modified"]

    def save(self, filepath):
        from avalon.fusion.pipeline import get_current_comp

        comp = get_current_comp()
        comp.Save(filepath)

    def open(self, filepath):

        # Hack to get fusion, see avalon.fusion.pipeline.get_current_comp()
        fusion = getattr(sys.modules["__main__"], "fusion", None)

        return fusion.LoadComp(filepath)

    def current_file(self):
        from avalon.fusion.pipeline import get_current_comp

        comp = get_current_comp()
        current_file = comp.GetAttrs()["COMPS_FileName"]
        if not current_file:
            return None

        # Normalize path to be safe.
        normalised = os.path.basename(os.path.normpath(current_file))

        return normalised

    def root(self):
        from avalon import api

        return os.path.join(api.Session["AVALON_WORKDIR"], "scenes")


class HoudiniHost(Host):
    """Houdini host integration"""

    @staticmethod
    def compatible():
        basename = os.path.basename(sys.executable).lower()
        if "houdini" in basename:
            return True

    def extensions(self):
        return [".hip", ".hiplc", ".hipnc"]

    def has_unsaved_changes(self):
        import hou
        return hou.hipFile.hasUnsavedChanges()

    def save(self, filepath):
        import hou

        # Force forwards slashes to avoid segfault
        filepath = filepath.replace("\\", "/")

        hou.hipFile.save(file_name=filepath,
                         save_to_recent_files=True)

        # Return a value so Workfiles App knows it worked
        return filepath

    def open(self, filepath):
        import hou

        # Force forwards slashes to avoid segfault
        filepath = filepath.replace("\\", "/")

        hou.hipFile.load(filepath,
                         suppress_save_prompt=True,
                         ignore_load_warnings=False)

        # Return a value so Workfiles App knows it worked
        return filepath

    def current_file(self):
        import hou

        current_file = hou.hipFile.path()
        if (os.path.basename(current_file) == "untitled.hip" and
                not os.path.exists(current_file)):
            # By default a new scene in houdini is saved in the current
            # working directory as "untitled.hip" so we need to capture
            # that and consider it 'not saved' when it's in that state.
            return None

        # Normalize path to be safe.
        normalised = os.path.basename(os.path.normpath(current_file))

        # Unsaved current file
        if normalised == ".":
            return None

        return normalised

    def root(self):
        from avalon import api

        return os.path.join(api.Session["AVALON_WORKDIR"], "scenes")
