"""Test pipeline.py

..note: These tests depend on global state and are therefore not reentrant.

"""

import os
import sys
import shutil
import tempfile

from maya import cmds, standalone
from mindbender.maya import pipeline, lib
import mindbender.api

from nose.tools import (
    assert_equals,
    with_setup
)

self = sys.modules[__name__]


def clear():
    for path in mindbender.api.registered_loaders_paths():
        mindbender.api.deregister_loaders_path()

    for fmt in mindbender.api.registered_formats():
        mindbender.api.deregister_format(fmt)


def setup():
    print("Initialising..")
    standalone.initialize()


def teardown():
    pass


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
    container = pipeline.containerise(name="Asset",
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


@with_setup(clear)
def test_load():
    """The maya.api.load triggers registered loaders automatically"""

    tempdir = tempfile.mkdtemp()

    loader = """
from mindbender import api
from maya import cmds

class DemoLoader(api.Loader):
    families = ["test.family"]

    def process(self, asset, subset, version, representation):
        cmds.file()

"""

    with open(os.path.join(tempdir, "my_loader.py"), "w") as f:
        f.write(loader)

    try:
        with mindbender.api.fixture(assets=["Asset1"], subsets=["subset1"]):
            asset = next(mindbender.api.ls(["assets"]))
            subset = asset["subsets"][0]
            version = subset["versions"][0]
            representation = version["representations"][0]

            assert_equals(asset["name"], "Asset1")
            assert_equals(subset["name"], "subset1")
            assert_equals(version["version"], 1)
            assert_equals(representation["format"], ".ma")

            version["families"] = ["test.family"]

            mindbender.api.register_format(".ma")
            pipeline.load(asset, subset)

    finally:
        shutil.rmtree(tempdir)
