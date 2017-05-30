"""Test pipeline.py

..note: These tests depend on global state and are therefore not reentrant.

"""

import os
import sys
import types
import shutil
import tempfile

from mindbender import pipeline

from nose.tools import (
    with_setup,
    assert_equals,
    assert_raises
)

self = sys.modules[__name__]


def clear():
    for path in pipeline.registered_loader_paths():
        pipeline.deregister_loader_path(path)


def setup():
    self.tempdir = tempfile.mkdtemp()
    pipeline.register_root(self.tempdir)

    # Mock host
    host = types.ModuleType("Test")
    host.__dict__.update({
        "ls": lambda: [],
        "create": lambda asset, subset, family, options: None,
        "load": lambda asset, subset, version, representation: None,
        "update": lambda container, version: None,
        "remove": lambda container: None,
    })

    pipeline.register_host(host)


def teardown():
    shutil.rmtree(self.tempdir)


@with_setup(clear)
def test_loaders():
    """Registering a path of loaders imports them appropriately"""

    tempdir = tempfile.mkdtemp()

    loader = """
from mindbender import api

class DemoLoader(api.Loader):
    def process(self, asset, subset, version, representation):
        pass

"""

    with open(os.path.join(tempdir, "my_loader.py"), "w") as f:
        f.write(loader)

    try:
        pipeline.register_loader_path(tempdir)
        loaders = pipeline.discover_loaders()

        assert "DemoLoader" in list(
            L.__name__ for L in loaders
        ), "Loader not found in %s" % ", ".join(
            l.__name__ for l in loaders)

    finally:
        shutil.rmtree(tempdir)
