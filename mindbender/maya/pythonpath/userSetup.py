"""Maya initialisation for Mindbender pipeline"""

from maya import cmds
import os

fps = os.getenv("MINDBENDER_FPS")


def setup():
    assert __import__("pyblish_maya").is_setup(), (
        "mindbender-core depends on pyblish_maya which has not "
        "yet been setup. Run pyblish_maya.setup()")

    from pyblish import api
    api.register_gui("pyblish_lite")

    from mindbender import api, maya
    api.install(maya)

    cmds.playbackOptions(edit=True, framesPerSecond=fps)

# Allow time for dependencies (e.g. pyblish-maya)
# to be installed first.
cmds.evalDeferred(setup)
