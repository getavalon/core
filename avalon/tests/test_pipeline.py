"""Test pipeline.py

..note: These tests depend on global state and are therefore not reentrant.

"""

import os
import sys
import types
import shutil
import tempfile

from avalon import pipeline

from nose.tools import (
    with_setup,
)

self = sys.modules[__name__]


def clear():
    for superclass, paths in pipeline.registered_plugin_paths().items():
        for path in paths:
            pipeline.deregister_plugin_path(superclass, path)


def setup():
    self.tempdir = tempfile.mkdtemp()
    pipeline.register_root(self.tempdir)

    # Mock host
    host = types.ModuleType("Test")
    host.__dict__.update({
        "ls": lambda: [],
        "create": lambda name, asset, family, options, data: None,
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
from avalon import api

class DemoLoader(api.Loader):
    def process(self, asset, subset, version, representation):
        pass

"""

    with open(os.path.join(tempdir, "my_loader.py"), "w") as f:
        f.write(loader)

    try:
        pipeline.register_plugin_path(pipeline.Loader, tempdir)
        loaders = pipeline.discover(pipeline.Loader)

        assert "DemoLoader" in list(
            L.__name__ for L in loaders
        ), "Loader not found in %s" % ", ".join(
            l.__name__ for l in loaders)

    finally:
        shutil.rmtree(tempdir)
