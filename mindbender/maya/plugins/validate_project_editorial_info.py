# validate_project_editorial_info.py
import pyblish.api


class ValidateMindbenderProjectEditInfo(pyblish.api.ContextPlugin):
    """
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
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        sceneIn = cmds.playbackOptions(query=True, animationStartTime=True)
        sceneOUT = cmds.playbackOptions(query=True, animationEndTime=True)
        sceneFPS = {
            "12fps" : 12,
            "game"  : 15,
            "film"  : 24,
            "pal"   : 25,
            "ntsc"  : 30,
            "show"  : 48,
            "palf"  : 50,
            "ntscf" : 60}.get(cmds.currentUnit(query=True, time=True))

        validFPS = context.data.get("project_fps")
        validEditIn = context.data.get("project_edit_in")
        validEditOut = context.data.get("project_edit_out")

        assert validFPS == sceneFPS, (
            ("The FPS is set to %s" % sceneFPS) +
            ("fps and not to %sfps" % validFPS))

        assert sceneIn == validEditIn, (
            "Animation Start is not set to \"%s\"" % validEditIn)

        assert sceneOUT == validEditOut, (
            "Animation End is not set to \"%s\"" % validEditOut)
