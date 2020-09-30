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
    assert_equals,
)

self = sys.modules[__name__]


def clear():
    for superclass, paths in pipeline.registered_plugin_paths().items():
        for path in paths:
            pipeline.deregister_plugin_path(superclass, path)

    pipeline._registered_event_handlers.clear()


def setup():
    self.tempdir = tempfile.mkdtemp()
    pipeline.register_root(self.tempdir)

    # Mock host
    dummy_maintained_selection = type(
        "empty_ctx", (object,),
        {"__enter__": lambda s: s, "__exit__": lambda *a, **k: None}
    )

    host = types.ModuleType("Test")
    host.__dict__.update({
        "ls": lambda: [],
        "maintained_selection": dummy_maintained_selection,
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
    def process(self, name, namespace, context):
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


@with_setup(clear)
def test_creators():
    """Register a Creator and create instance by different family input"""

    class BarCreator(pipeline.Creator):
        def process(self):
            return True
        family = "bar"

    pipeline.register_plugin(pipeline.Creator, BarCreator)

    # Create with regular string type family
    assert pipeline.create("foo", "my_asset", family="bar")
    # Create with plugin class, see getavalon/core#531
    assert pipeline.create("foo", "my_asset", family=BarCreator)


@with_setup(clear)
def test_on():
    """api.on() works as advertised"""

    count = {"#": 0}

    def on_event():
        count["#"] += 1

    pipeline.on("some_event", on_event)
    assert_equals(count["#"], 0)
    pipeline.emit("some_event")
    assert_equals(count["#"], 1)


@with_setup(clear)
def test_on_with_failing_callback():
    """api.on() runs all callbacks, regardless of some failing"""

    count = {"#": 0}

    def bad_event():
        count["#"] -= 1
        raise Exception("I'm a dick")

    def good_event():
        count["#"] += 1

    pipeline.on("some_event", bad_event)
    pipeline.on("some_event", good_event)
    assert_equals(count["#"], 0)
    pipeline.emit("some_event")
    assert_equals(count["#"], 0)


@with_setup(clear)
def test_on_with_garbage_callback():
    """api.on() runs all callbacks, unless they've been garbage collected"""

    count = {"#": 0}

    def on_goodbye():
        count["#"] += 1

    pipeline.on("some_event", on_goodbye)
    assert_equals(count["#"], 0)
    pipeline.emit("some_event")
    assert_equals(count["#"], 1)
    del on_goodbye
    pipeline.emit("some_event")
    assert_equals(count["#"], 1)
