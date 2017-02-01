"""Maya initialisation for Mindbender pipeline"""

from maya import cmds

import os


def mayafpsconverter(Sfps):
    condition = 0
    if Sfps is None:
        return ""
    if Sfps == "":
        condition = 1
        return Sfps
    if Sfps == "15":
        condition = 1
        return "game"
    if Sfps == "24":
        condition = 1
        return "film"
    if Sfps == "25":
        condition = 1
        return "pal"
    if Sfps == "30":
        condition = 1
        return "ntsc"
    if Sfps == "48":
        condition = 1
        return "show"
    if Sfps == "50":
        condition = 1
        return "palf"
    if Sfps == "60":
        condition = 1
        return "ntscf"
    ERRORSTRING = "MINDBENDER_FPS has bad value in the bat file"
    if str(Sfps).isdigit() is False:
        cmds.confirmDialog(title="Enviroment variable error",
                           message=ERRORSTRING,
                           button="",
                           defaultButton="",
                           cancelButton="",
                           dismissString="")
        return ""
    if condition == 0:
        Sfps = str(Sfps) + "fps"
        return Sfps


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
