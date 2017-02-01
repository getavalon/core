"""Maya initialisation for Mindbender pipeline"""

from maya import cmds

import os
import mayafpsconverter


MINDBENDER_FPS = mayafpsconverter(os.getenv("MINDBENDER_FPS"))
MINDBENDER_EDIT_IN = os.getenv("MINDBENDER_EDIT_IN")
MINDBENDER_EDIT_OUT = os.getenv("MINDBENDER_EDIT_OUT")
MINDBENDER_RESOLUTION_WIDTH = os.getenv("MINDBENDER_RESOLUTION_WIDTH")
MINDBENDER_RESOLUTION_HEIGHT = os.getenv("MINDBENDER_RESOLUTION_HEIGHT")


def setup():
    assert __import__("pyblish_maya").is_setup(), (
        "mindbender-core depends on pyblish_maya which has not "
        "yet been setup. Run pyblish_maya.setup()")

    from pyblish import api
    api.register_gui("pyblish_lite")

    from mindbender import api, maya
    api.install(maya)


# Allow time for dependencies (e.g. pyblish-maya)
# to be installed first.
cmds.evalDeferred(setup)
if not MINDBENDER_FPS == "":
    cmds.currentUnit(time=MINDBENDER_FPS)
if not MINDBENDER_EDIT_IN == "":
    cmds.playbackOption(animationEndTime=MINDBENDER_EDIT_IN)
if not MINDBENDER_EDIT_OUT == "":
    cmds.playbackOption(animationEndTime=MINDBENDER_EDIT_OUT)
