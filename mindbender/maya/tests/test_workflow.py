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

from mindbender import api, maya, io, inventory, schema

from nose.tools import (
    with_setup,
    assert_equals,
)

IS_SILENT = bool(os.getenv("MINDBENDER_SILENT"))
PROJECT_NAME = "hulk"
ASSET_NAME = "Bruce"
TASK_NAME = "modeling"

self = sys.modules[__name__]
self._tempdir = None
self._config = {
    "schema": "mindbender-core:config-1.0",
    "apps": [
        {"name": "app1"},
    ],
    "tasks": [
        {"name": "task1"},
    ],
    "template": {
        "work":
            "{root}/{project}/{silo}/{asset}/work/"
            "{task}/{user}/{app}",
        "publish":
            "{root}/{project}/{silo}/{asset}/publish/"
            "{subset}/v{version:0>3}/{subset}.{representation}"
    },
    "copy": {}
}
self._inventory = {
    "schema": "mindbender-core:inventory-1.0",
    "assets": [
        {"name": ASSET_NAME},
    ],
    "film": []
}


def setup():
    self._tempdir = tempfile.mkdtemp()
    api.register_root(self._tempdir)

    # Setup environment
    os.environ["MINDBENDER_PROJECT"] = PROJECT_NAME
    os.environ["MINDBENDER_ASSET"] = ASSET_NAME
    os.environ["MINDBENDER_TASK"] = TASK_NAME
    os.environ["MINDBENDER_ASSETPATH"] = (
        "{root}/{project}/{silo}/{asset}".format(
            root=api.registered_root(),
            project=PROJECT_NAME,
            asset=ASSET_NAME,
            silo="assets"
        ))
    os.environ["MINDBENDER_SILO"] = "assets"

    pyblish_maya.setup()
    api.install(maya)
    io.activate_project(PROJECT_NAME)

    schema.validate(self._config)
    schema.validate(self._inventory)

    inventory.save(
        name=PROJECT_NAME,
        config=self._config,
        inventory=self._inventory
    )


def teardown():
    pyblish_maya.teardown()
    io.drop()
    api.uninstall()

    shutil.rmtree(self._tempdir)


def clear():
    shutil.rmtree(self._tempdir)
    self._tempdir = tempfile.mkdtemp()

    cmds.file(new=True, force=True)
    cmds.file(rename="temp.ma")


def publish():
    context = pyblish.util.publish()

    header = "{:<10}{:<40} -> {}".format("Success", "Plug-in", "Instance")
    result = "{success:<10}{plugin.__name__:<40} -> {instance}"
    error = "{:<10}+-- EXCEPTION: {:<70} line {:<20}"
    record = "{:<10}+-- {level}: {message:<70}"

    results = list()
    for r in context.data["results"]:
        # Format summary
        results.append(result.format(**r))

        # Format log records
        for lr in r["records"]:
            results.append(
                record.format(
                    "",
                    level=lr.levelname,
                    message=lr.msg))

        # Format exception (if any)
        if r["error"]:
            _, line, _, _ = r["error"].traceback
            results.append(error.format("", r["error"], line))

    report = """
{header}
{line}
{results}
    """

    if not IS_SILENT:
        print(report.format(header=header,
                            results="\n".join(results),
                            line="-" * 70))

    return context


@with_setup(clear)
def test_modeling():
    """Modeling workflow is functional"""
    transform, generator = cmds.polyCube(name="body_PLY")
    group = cmds.group(transform, name="ROOT")

    cmds.select(group, replace=True)
    maya.create(
        name="modelDefault",
        asset=ASSET_NAME,
        family="mindbender.model",
        options={"useSelection": True}
    )

    # Comply with save validator
    cmds.file(save=True)

    publish()

    asset = io.find_one({
        "type": "asset",
        "name": ASSET_NAME
    })

    assert asset

    subset = io.find_one({
        "parent": asset["_id"],
        "type": "subset",
        "name": "modelDefault"
    })

    assert subset

    version = io.find_one({
        "parent": subset["_id"],
        "type": "version",
    })

    assert version

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

    maya.create(
        name="animationDefault",
        asset=ASSET_NAME,
        family="mindbender.animation",
        options={"useSelection": True}
    )

    cmds.file(save=True)

    publish()

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

    assert version

    representation = io.find_one({
        "parent": version["_id"],
        "type": "representation",
        "name": "abc"
    })

    assert representation is not None

    container = maya.load(representation)
    nodes = cmds.sets(container, query=True)
    print("Nodes: %s" % nodes)
    cube = cmds.ls(nodes, type="mesh")
    transform = cmds.listRelatives(cube, parent=True)[0]

    for time, value in visibility_keys:
        cmds.currentTime(time, edit=True)
        assert cmds.getAttr(transform + ".visibility") == value, (
            "Cached visibility did not match original visibility")


@with_setup(clear)
def test_update():
    """Updating works"""

    transform, generator = cmds.polyCube(name="body_PLY")
    group = cmds.group(transform, name="ROOT")

    cmds.select(group, replace=True)
    maya.create(
        name="modelDefault",
        asset=ASSET_NAME,
        family="mindbender.model",
        options={"useSelection": True}
    )

    # Comply with save validator
    cmds.file(save=True)

    publish()
    publish()
    publish()  # Version 3

    cmds.file(new=True, force=True)

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
        "name": 2
    })

    assert version

    representation = io.find_one({
        "parent": version["_id"],
        "type": "representation",
        "name": "ma"
    })

    maya.load(representation["_id"])
    container = next(maya.ls())
    maya.update(container, 3)


@with_setup(clear)
def test_update_imported():
    """You cannot update an imported container"""


@with_setup(clear)
def test_modeling_to_rigging():
    transform, generator = cmds.polyCube(name="body_PLY")
    group = cmds.group(transform, name="ROOT")

    cmds.select(group, replace=True)
    maya.create(
        name="modelDefault",
        asset=ASSET_NAME,
        family="mindbender.model",
        options={"useSelection": True})

    # Comply with save validator
    cmds.file(save=True)

    publish()

    cmds.file(new=True, force=True)

    representation = io.locate([
        PROJECT_NAME, ASSET_NAME, "modelDefault", 1, "ma"
    ])

    container = maya.load(representation)
    nodes = cmds.sets(container, query=True)
    assembly = cmds.ls(nodes, assemblies=True)[0]
    assert_equals(assembly, "Bruce_01_:modelDefault")

    # Rig it
    mesh = cmds.ls(nodes, type="mesh")
    transform = cmds.listRelatives(mesh, parent=True)[0]
    ctrl = cmds.circle(name="main_CTL")
    cmds.parentConstraint(ctrl, transform)

    cmds.select([assembly] + ctrl, replace=True)
    group = cmds.group(name="ROOT")

    cmds.select(mesh, replace=True)

    out_set = cmds.sets(name="out_SET")

    cmds.select(ctrl)
    controls_set = cmds.sets(name="controls_SET")

    cmds.select([group, out_set, controls_set], noExpand=True)
    maya.create(
        name="rigDefault",
        asset=os.environ["MINDBENDER_ASSET"],
        family="mindbender.rig",
        options={"useSelection": True},
    )

    cmds.file(rename="temp.ma")
    cmds.file(save=True)

    publish()

    cmds.file(new=True, force=True)

    representation = io.locate([
        PROJECT_NAME, ASSET_NAME, "rigDefault", 1, "ma"
    ])

    container = maya.load(representation)
    nodes = cmds.sets(container, query=True)
    assembly = cmds.ls(nodes, assemblies=True)[0]
    assert_equals(assembly, "Bruce_01_:rigDefault")
