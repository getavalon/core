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
    os.environ["ASSETDIR"] = assetdir
    os.environ["MINDBENDER_SILO"] = "assets"


def teardown():
    pyblish_maya.teardown()
    api.uninstall()

    shutil.rmtree(self.tempdir)


def clear():
    cmds.file(new=True, force=True)


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
    cmds.file(rename="temp.ma")
    cmds.file(save=True)

    # Comply with ID validator
    cmds.addAttr(transform, longName="mbID", dataType="string")

    pyblish.util.publish()

    asset = next(api.ls())
    assert_equals(asset["name"], "Test")

    subset = asset["subsets"][0]
    assert_equals(subset["name"], "modelDefault")

    version = subset["versions"][0]
    assert_equals(version["version"], 1)

    representation = version["representations"][0]
    assert_equals(representation["format"], ".ma")
