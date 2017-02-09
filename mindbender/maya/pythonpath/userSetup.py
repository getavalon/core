"""Maya initialisation for Mindbender pipeline"""

from maya import cmds

import os


def mayafpsconverter(fps):
    ERRORSTRING = "MINDBENDER_FPS has bad value in the bat file"
    if str(fps).isdigit() is False:
        cmds.confirmDialog(title="Enviroment variable error",
                           message=ERRORSTRING,
                           button="",
                           defaultButton="",
                           cancelButton="",
                           dismissString="")
        return ""
    return {
        "15": "game",
        "24": "film",
        "25": "pal",
        "30": "ntsc",
        "48": "show",
        "50": "palf",
        "60": "ntscf",
        None: "",
        "": "", }.get(fps, fps + "fps")


def setup():
    assert __import__("pyblish_maya").is_setup(), (
        "mindbender-core depends on pyblish_maya which has not "
        "yet been setup. Run pyblish_maya.setup()")

    from pyblish import api
    api.register_gui("pyblish_lite")

    from mindbender import api, maya
    api.install(maya)

    MINDBENDER_FPS = os.getenv("MINDBENDER_FPS")
    MINDBENDER_EDIT_IN = os.getenv("MINDBENDER_EDIT_IN")
    MINDBENDER_EDIT_OUT = os.getenv("MINDBENDER_EDIT_OUT")
    MINDBENDER_RESOLUTION_WIDTH = os.getenv("MINDBENDER_RESOLUTION_WIDTH")
    MINDBENDER_RESOLUTION_HEIGHT = os.getenv("MINDBENDER_RESOLUTION_HEIGHT")

    if MINDBENDER_FPS is not None:
        cmds.currentUnit(time=(mayafpsconverter(MINDBENDER_FPS)))
    if MINDBENDER_EDIT_IN is not None:
        cmds.playbackOptions(animationStartTime=MINDBENDER_EDIT_IN)
    if MINDBENDER_EDIT_OUT is not None:
        cmds.playbackOptions(animationEndTime=MINDBENDER_EDIT_OUT)


# Allow time for dependencies (e.g. pyblish-maya)
# to be installed first.
cmds.evalDeferred(setup)
