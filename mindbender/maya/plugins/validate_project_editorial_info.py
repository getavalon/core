# validate_project_editorial_info.py
import pyblish.api


class ValidateMindbenderProjectEditInfo(pyblish.api.ContextPlugin):
    """ Checks your scene with editorial info

    All the info that gets validated
    has been set by the projects
    bat files.
    If you are surtain that the info
    is incorrect, talk to
    project Supervisor with haste !

    """

    label = "Validate Project Edit Info"
    optional = True
    order = pyblish.api.ValidatorOrder

    def process(self, context):
        from maya import cmds

        scene_in = cmds.playbackOptions(query=True, animationStartTime=True)
        scene_out = cmds.playbackOptions(query=True, animationEndTime=True)
        scene_fps = {
                "12fps" : 12,
                "16fps" : 16,
                "game"  : 15,
                "film"  : 24,
                "pal"   : 25,
                "ntsc"  : 30,
                "show"  : 48,
                "palf"  : 50,
                "ntscf" : 60}.get(cmds.currentUnit(query=True, time=True))

        if scene_fps is None:
            scene_fps = "New Value"

        valid_fps = context.data.get("project_fps")
        valid_edit_in = context.data.get("project_edit_in")
        valid_edit_out = context.data.get("project_edit_out")

        assert valid_fps == scene_fps, (
            "The FPS is set to %sfps and not to %sfps"
            % (scene_fps, valid_fps))

        assert scene_in == valid_edit_in, (
            "Animation Start is set to %s and not set to \"%s\""
            % (scene_in, valid_edit_in))

        assert scene_out == valid_edit_out, (
            "Animation End is set to %s and not set to \"%s\""
            % (scene_out, valid_edit_out))
