"""Integration tests

These tests include external libraries in order to test
the integration between them.

"""

import os
import sys
import shutil
import tempfile

from maya import cmds

import pyblish_maya
import pyblish.api
import pyblish.util

from mindbender import api, maya, io, inventory
from mindbender.vendor import toml

from nose.tools import (
    with_setup
)

PROJECT_NAME = "hulk"
ASSET_NAME = "Bruce"

self = sys.modules[__name__]
self.tempdir = None

self._inventory = """\
schema = "mindbender-core:inventory-1.0"

[assets.%s]
label = "Bruce Wayne"
""" % ASSET_NAME

self._config = """\
schema = "mindbender-core:config-1.0"

[metadata]
name = "%s"
fps = 25
resolution_width = 1920
resolution_height = 1080
label = "The Hulk"

[template]
work = "{root}/{project}/{silo}/{asset}/work/{task}/{user}/{app}"
publish = "{root}/{project}/{silo}/{asset}/publish/{subset}/v{version:0>3}/{subset}.{representation}"

[apps.maya2016]
label = "Autodesk Maya 2016"

[apps.nuke10]
label = "The Foundry Nuke 10.0"

[tasks.modeling]
[tasks.animation]
[tasks.rigging]
[tasks.lighting]
[tasks.lookdev]
[tasks.layout]
""" % PROJECT_NAME


def setup():
    pyblish_maya.setup()
    api.install(maya)

    io.install(collection="test")

    self.tempdir = tempfile.mkdtemp()

    with open(os.path.join(self.tempdir, ".inventory.toml"), "w") as f:
        toml.dump(toml.loads(self._inventory), f)

    with open(os.path.join(self.tempdir, ".config.toml"), "w") as f:
        toml.dump(toml.loads(self._config), f)

    inventory.save(self.tempdir)
    api.register_root(self.tempdir)

    project = io.find_one({
        "type": "project",
        "name": PROJECT_NAME
    })

    asset = io.find_one({
        "type": "asset",
        "parent": project["_id"],
        "name": ASSET_NAME
    })

    # Setup environment
    os.environ["MINDBENDER__PROJECT"] = str(project["_id"])
    os.environ["MINDBENDER__ASSET"] = str(asset["_id"])
    os.environ["MINDBENDER_ASSET"] = asset["name"]
    os.environ["MINDBENDER_ASSETPATH"] = os.path.join(
        self.tempdir,
        "assets",
        ASSET_NAME
    )
    os.environ["MINDBENDER_SILO"] = "assets"

    print(list(io.find({})))


def teardown():
    pyblish_maya.teardown()
    api.uninstall()

    shutil.rmtree(self.tempdir)

    io.drop()


def clear():
    shutil.rmtree(self.tempdir)
    self.tempdir = tempfile.mkdtemp()

    cmds.file(new=True, force=True)
    cmds.file(rename="temp.ma")


@with_setup(clear)
def test_modeling():
    """Modeling workflow is functional"""
    transform, generator = cmds.polyCube(name="body_PLY")
    group = cmds.group(transform, name="ROOT")

    cmds.select(group, replace=True)
    maya.create("modelDefault",
                family="mindbender.model",
                options={"useSelection": True})

    # Comply with save validator
    cmds.file(save=True)

    pyblish.util.publish()

    asset = io.find_one({
        "type": "asset",
        "name": ASSET_NAME
    })

    subset = io.find_one({
        "parent": asset["_id"],
        "type": "subset",
        "name": "modelDefault"
    })

    version = io.find_one({
        "parent": subset["_id"],
        "type": "version",
        "name": 1
    })

    assert io.find_one({
        "parent": version["_id"],
        "type": "representation",
        "name": "ma"
    }) is not None


@with_setup(clear)
def test_alembic_export():
    """Exporting Alembic works"""

    cube, generator = cmds.polyCube(name="myCube_GEO")
    transform = cmds.ls(selection=True)

    visibility_keys = [
        (10, True),
        (20, False),
        (30, True)
    ]

    for time, value in visibility_keys:
        cmds.setKeyframe(transform,
                         time=time,
                         attribute="visibility",
                         value=value)

    cmds.group(name="ROOT")

    maya.create(
        "animationDefault",
        family="mindbender.animation",
        options={"useSelection": True}
    )

    cmds.file(save=True)

    pyblish.util.publish()

    # Import and test result
    cmds.file(new=True, force=True)

    asset = io.find_one({
        "type": "asset",
        "name": ASSET_NAME
    })

    subset = io.find_one({
        "parent": asset["_id"],
        "type": "subset",
        "name": "animationDefault"
    })

    version = io.find_one({
        "parent": subset["_id"],
        "type": "version",
        "name": 1
    })

    representation = io.find_one({
        "parent": version["_id"],
        "type": "representation",
        "name": "abc"
    })

    assert representation is not None

    container = maya.load(representation)

    cube = cmds.ls(container, type="mesh")
    transform = cmds.listRelatives(cube, parent=True)[0]

    for time, value in visibility_keys:
        cmds.currentTime(time, edit=True)
        assert cmds.getAttr(transform + ".visibility") == value, (
            "Cached visibility did not match original visibility")
