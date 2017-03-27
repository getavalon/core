# validate_project_editorial_info.py
import pyblish.api


class ValidateMindbenderProjectEditInfo(pyblish.api.ContextPlugin):
    """Checks your scene with editorial info

    All the info that gets validated has been set by the projects bat files.
    If you are certain that the info is incorrect, talk to your project
    Supervisor with haste!
    """

    label = "Validate Project Edit Info"
    optional = True
    order = pyblish.api.ValidatorOrder
    families = ["mindbender.animation"]

    def process(self, context):
        from maya import cmds

        scene_in = cmds.playbackOptions(query=True, animationStartTime=True)
        scene_out = cmds.playbackOptions(query=True, animationEndTime=True)
        scene_fps = {
                "12fps" : 12,
                "game"  : 15,
                "16fps" : 16,
                "film"  : 24,
                "pal"   : 25,
                "ntsc"  : 30,
                "show"  : 48,
                "palf"  : 50,
                "ntscf" : 60}.get(cmds.currentUnit(query=True, time=True))

        if scene_fps is None:
            scene_fps = "a strange "

        env = context.data.get("environment", dict())

        valid_fps = env.get("mindbenderFps")
        valid_edit_in = env.get("mindbenderEditIn")
        valid_edit_out = env.get("mindbenderEditOut")

        skip_on_none = [valid_fps, valid_edit_in, valid_edit_out]

        if None in skip_on_none:
            self.log.debug(" environment not set")
            return

        assert int(valid_fps) == int(scene_fps), (
            "The FPS is set to %sfps and not to %sfps"
            % (scene_fps, valid_fps))

        assert int(scene_in) == int(valid_edit_in), (
            "Animation Start is set to %s and not set to \"%s\""
            % (scene_in, valid_edit_in))

        assert int(scene_out) == int(valid_edit_out), (
            "Animation End is set to %s and not set to \"%s\""
            % (scene_out, valid_edit_out))
