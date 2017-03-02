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

from mindbender import api, maya

from nose.tools import (
    assert_equals,
    with_setup
)

self = sys.modules[__name__]
self.tempdir = None


def setup():
    pyblish_maya.setup()
    api.install(maya)

    self.tempdir = tempfile.mkdtemp()

    assetdir = os.path.join(
        self.tempdir,
        "assets",
        "Test"
    )

    os.makedirs(assetdir)

    api.register_root(self.tempdir)
    assert api.registered_root() == self.tempdir
    api.register_silo("assets")

    # Setup environment
    os.environ["MINDBENDER_ASSETPATH"] = assetdir
    os.environ["MINDBENDER_SILO"] = "assets"


def teardown():
    pyblish_maya.teardown()
    api.uninstall()

    shutil.rmtree(self.tempdir)


def clear():
    shutil.rmtree(self.tempdir)
    self.tempdir = tempfile.mkdtemp()

    cmds.file(new=True, force=True)
    cmds.file(rename="temp.ma")


def test_setup():
    """Fixture is setup ok"""
    assert_equals(next(api.ls())["name"], "Test")


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

    asset = next(api.ls())
    assert_equals(asset["name"], "Test")

    subset = asset["subsets"][0]
    assert_equals(subset["name"], "modelDefault")

    version = subset["versions"][0]
    assert_equals(version["version"], 1)

    representation = version["representations"][0]
    assert_equals(representation["format"], ".ma")


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

    asset = next(api.ls())
    assert_equals(asset["name"], "Test")

    subset = asset["subsets"][0]
    assert_equals(subset["name"], "animationDefault")

    version = subset["versions"][0]
    assumed_version = 1
    assert_equals(version["version"], assumed_version)

    # There may be more than one representation, such as .source
    representation = next(r for r in version["representations"]
                          if r["format"] == ".abc")

    container = maya.load(asset, subset, assumed_version, representation)

    cube = cmds.ls(container, type="mesh")
    transform = cmds.listRelatives(cube, parent=True)[0]

    for time, value in visibility_keys:
        cmds.currentTime(time, edit=True)
        assert cmds.getAttr(transform + ".visibility") == value, (
            "Cached visibility did not match original visibility")
