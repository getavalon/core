"""Test pipeline.py

..note: These tests depend on global state and are therefore not reentrant.

"""

import os
import sys
import shutil
import tempfile

from maya import cmds

from mindbender.maya import pipeline
import mindbender.api

from nose.tools import (
    assert_equals,
    with_setup
)

self = sys.modules[__name__]


def clear():
    cmds.file(new=True, force=True)

    for path in mindbender.api.registered_loader_paths():
        mindbender.api.deregister_loader_path(path)

    for fmt in mindbender.api.registered_formats():
        mindbender.api.deregister_format(fmt)
