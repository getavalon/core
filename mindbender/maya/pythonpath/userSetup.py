"""Maya initialisation for Mindbender pipeline"""

import os
from maya import cmds


def setup():
    from pyblish import api as pyblish
    pyblish.register_gui("pyblish_qml")

    import pyblish_maya
    assert pyblish_maya.is_setup(), (
        "pyblish-mindbender depends on pyblish_maya which has not "
        "yet been setup. Run pyblish_maya.setup()")

    from mindbender import install, maya, api as mindbender
    install(maya)

    # Mindbender integrates to "root", which we define to be the
    # full path to ROOT. ROOT is set during application launch,
    # via the corresponding .bat file, e.g. maya__projectA.bat

    assert os.getenv("ROOT"), "Missing environment variable 'ROOT'"
    mindbender.register_root(os.getenv("ROOT"))

    # Default Data
    mindbender.register_data(key="id", value="pyblish.mindbender.instance")
    mindbender.register_data(key="name", value="{name}")
    mindbender.register_data(key="subset", value="{name}")
    mindbender.register_data(key="family", value="{family}")

    # Default families
    mindbender.register_family(
        name="mindbender.model",
        help="Polygonal geometry for animation"
    )

    mindbender.register_family(
        name="mindbender.rig",
        help="Character rig"
    )

    mindbender.register_family(
        name="mindbender.animation",
        help="Pointcache"
    )


# Allow time for dependencies (e.g. pyblish-maya)
# to be installed first.
cmds.evalDeferred(setup)
