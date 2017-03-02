"""Test pipeline.py

..note: These tests depend on global state and are therefore not reentrant.

"""

import sys

from maya import cmds

import pyblish_maya
from mindbender.maya import pipeline
from mindbender import api, maya

from nose.tools import (
    assert_equals,
)

self = sys.modules[__name__]


def setup():
    pyblish_maya.setup()
    api.install(maya)


def clear():
    cmds.file(new=True, force=True)

    for path in api.registered_loader_paths():
        api.deregister_loader_path(path)

    for fmt in api.registered_formats():
        api.deregister_format(fmt)


def test_load_version():
    """Versions may be loaded as either object or integer"""

    print(api.registered_loader_paths())
    print(api.discover_loaders())
    with api.fixture(assets=["Asset1"],
                     subsets=["modelDefault"],
                     versions=3):
        asset = next(api.ls(["assets"]))
        subset = asset["subsets"][0]
        version = subset["versions"][0]
        representation = version["representations"][0]

        print("Loading as objects works.")
        cmds.file(new=True, force=True)
        pipeline.load(asset, subset, version, representation)
        container = next(pipeline.ls())

        for key, value in {"asset": "Asset1",
                           "subset": "modelDefault",
                           "version": 1,
                           "representation": ".ma"}.items():
            assert_equals(container[key], value)

        print("Loading version as integer works.")
        cmds.file(new=True, force=True)
        pipeline.load(asset, subset, 3, representation)
        container = next(pipeline.ls())

        for key, value in {"asset": "Asset1",
                           "subset": "modelDefault",
                           "version": 3,
                           "representation": ".ma"}.items():
            assert_equals(container[key], value)


def test_load_representation():
    """Representations may be loaded as either object or string"""

    with api.fixture(assets=["Asset1"],
                     subsets=["modelDefault"],
                     versions=1):
        asset = next(api.ls(["assets"]))
        subset = asset["subsets"][0]
        version = subset["versions"][0]
        representation = version["representations"][0]

        print("Loading representation as object works.")
        cmds.file(new=True, force=True)
        pipeline.load(asset, subset, 1, representation)

        container = next(pipeline.ls())
        for key, value in {"asset": "Asset1",
                           "subset": "modelDefault",
                           "version": 1,
                           "representation": ".ma"}.items():
            assert_equals(container[key], value)

        print("Loading representation as string works.")
        cmds.file(new=True, force=True)
        pipeline.load(asset, subset, 1, ".ma")

        container = next(pipeline.ls())
        for key, value in {"asset": "Asset1",
                           "subset": "modelDefault",
                           "version": 1,
                           "representation": ".ma"}.items():
            assert_equals(container[key], value)
