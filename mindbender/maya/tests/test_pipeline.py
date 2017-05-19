"""Test pipeline.py

..note: These tests depend on global state and are therefore not reentrant.

"""

import os
import sys

from maya import cmds

import pyblish_maya
from mindbender import api, maya

self = sys.modules[__name__]


def setup():
    pyblish_maya.setup()
    os.environ["MINDBENDER_PROJECT"] = "testProject"
    os.environ["MINDBENDER_ASSET"] = "testAsset"

    api.install(maya)


def clear():
    cmds.file(new=True, force=True)

    for path in api.registered_loader_paths():
        api.deregister_loader_path(path)

    for fmt in api.registered_formats():
        api.deregister_format(fmt)


def test_load_version():
    """Versions may be loaded as either object or integer"""
    pass


def test_load_representation():
    """Representations may be loaded as either object or string"""
    pass
