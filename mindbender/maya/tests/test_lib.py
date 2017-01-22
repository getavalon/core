
from maya import cmds
from mindbender.maya import pipeline, lib

from nose.tools import (
    assert_equals,
)


def test_containerise():
    """A containerised asset should appear in maya.ls()"""
    asset = {
        "schema": "mindbender-core:asset-1.0",
        "name": "Doe",
        "subsets": [],
    }

    subset = {
        "schema": "mindbender-core:subset-1.0",
        "name": "modelDefault",
        "versions": [],
    }

    version = {
        "schema": "mindbender-core:version-1.0",
        "version": 2,
        "path": "{root}/this.ma",
        "time": "2017Z5454542",
        "author": "Doe",
        "source": "{root}/some/dir/file.ma",
    }

    representation = {
        "schema": "mindbender-core:representation-1.0",
        "format": ".ma",
        "path": "{dirname}/lookdevDefault{format}",
    }

    node = cmds.createNode("transform", name="Group")
    container = lib.containerise(name="Asset",
                                 namespace="Asset01_",
                                 nodes=[node],
                                 asset=asset,
                                 subset=subset,
                                 version=version,
                                 representation=representation,
                                 suffix="_CON")
    assert_equals(container, "Asset_CON")

    print(lib.lsattr("id", "pyblish.mindbender.container"))

    containers = list(c["name"] for c in pipeline.ls())
    assert "Asset01_" in containers, containers
