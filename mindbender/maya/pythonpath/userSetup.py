"""Maya initialisation for Mindbender pipeline"""

from maya import cmds


def setup():
    assert __import__("pyblish_maya").is_setup(), (
        "pyblish-mindbender depends on pyblish_maya which has not "
        "yet been setup. Run pyblish_maya.setup()")

    from pyblish import api
    api.register_gui("pyblish_lite")

    from mindbender import api, maya
    api.install(maya)


# Allow time for dependencies (e.g. pyblish-maya)
# to be installed first.
cmds.evalDeferred(setup)
