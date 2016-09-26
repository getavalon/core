"""Test pipeline.py

..note: These tests depend on global state and are therefore not reentrant.

"""

import os
import sys
import json
import types
import shutil
import tempfile
import contextlib

from pyblish_starter import pipeline, lib

from nose.tools import assert_equals, assert_raises

self = sys.modules[__name__]


def setup():
    self.tempdir = tempfile.mkdtemp()
    pipeline.register_root(self.tempdir)

    # Mock host
    host = types.ModuleType("Test")
    host.__dict__.update({
        "create": lambda *args, **kwargs: None,
        "load": lambda *args, **kwargs: None,
    })

    pipeline.register_host(host)


def teardown():
    shutil.rmtree(self.tempdir)


@contextlib.contextmanager
def bad_fixture():
    empty = os.path.join(self.tempdir, "empty")
    os.makedirs(empty)

    try:
        yield
    finally:
        shutil.rmtree(empty)


def test_ls():
    """ls() returns available assets from current root directory

    ls() returns a formatted list of available assets. For an asset
    to be recognised as an asset, it must adhere to a strict schema.

     ________________________________ ________________________________
    |          |          |          |          |          |          |
    | version1 | version2 | version3 | version1 | version2 | version3 |
    |__________|__________|__________|__________|__________|__________|
    |                                |                                |
    |            asset1              |             asset2             |
    |________________________________|________________________________|
    |                                                                 |
    |                             project                             |
    |_________________________________________________________________|

    This schema is located within each version of an asset and is
    denoted `pyblish-starter:version-1.0`.

    The members of this schema is also strict, they are:

    {
        "schema": "pyblish-starter:version-1.0",
        "name": "Name of asset",
        "representations": [List of representations],
    }

    Where each `representation` follows the following schema.

    {
        "format": "file extension or similar identifier",
        "source": "absolute path to source file",
        "author": "original author of version",
        "path": "relative path to file, starting at {root}"
    }

    The returned dictionary is also strictly defined.

    """

    with pipeline.fixture() as root:
        asset = next(pipeline.ls())

    reference = {
        "schema": "pyblish-starter:asset-1.0",
        "name": "Asset1",
        "versions": [
            {
                "schema": "pyblish-starter:version-1.0",
                "version": 1,
                "path": os.path.join(
                    root,
                    "shared",
                    "Asset1",
                    "v001"
                ),
                "source": os.path.join(
                    "{project}",
                    "maya",
                    "scenes",
                    "scene.ma"
                ),
                "representations": [
                    {
                        "schema": "pyblish-starter:representation-1.0",
                        "format": ".ma",
                        "path": os.path.join(
                            "{dirname}",
                            "Asset1{format}"
                        ),
                    }
                ],
                "time": "",
                "author": "mottosso",
            },
        ]
    }

    # Printed on error
    print("# Comparing result:")
    print(json.dumps(asset, indent=4, sort_keys=True))
    print("# With reference:")
    print(json.dumps(reference, indent=4, sort_keys=True))

    assert_equals(asset, reference)


def test_ls_returns_sorted_versions():
    """Versions returned from ls() are alphanumerically sorted"""
    with pipeline.fixture(versions=1):
        for asset in pipeline.ls():
            previous_version = 0
            for version in asset["versions"]:
                version = version["version"]
                assert version > previous_version
                previous_version = version


def test_ls_empty():
    """No assets results in an empty generator"""
    with pipeline.fixture(assets=[], versions=0):
        assert_raises(StopIteration, next, pipeline.ls())


def test_ls_no_shareddir():
    """A root without /shared returns an empty generator"""

    with bad_fixture():
        assert next(pipeline.ls(), None) is None
