import os
import sys
import json
import types
import shutil
import tempfile
import contextlib

import pyblish_starter

from nose.tools import assert_equals

self = sys.modules[__name__]


@contextlib.contextmanager
def root(root):
    host = pyblish_starter.registered_host()
    old = host.root
    host.root = lambda: root

    try:
        yield
    finally:
        host.root = old


def setup():
    self.tempdir = tempfile.mkdtemp()
    _register_host()
    _generate_fixture()


def teardown():
    shutil.rmtree(self.tempdir)
    sys.stdout.write("Removed temporary directory \"%s\"" % self.tempdir)


def _register_host():
    host = types.ModuleType("Test")
    host.__dict__.update({
        "root": lambda: self.tempdir,
        "create": lambda *args, **kwargs: None,
        "load": lambda *args, **kwargs: None,
    })

    pyblish_starter.register_host(host)


def _generate_fixture():
    root = os.path.join(
        self.tempdir,
        "shared"
    )

    for asset in ("Asset1",):
        assetdir = os.path.join(root, asset)
        os.makedirs(assetdir)

        if asset == "BadAsset":
            # An asset must have at least one version
            continue

        for version in ("v001",):
            versiondir = os.path.join(assetdir, version)
            os.makedirs(versiondir)

            fname = os.path.join(versiondir, asset + ".ma")
            open(fname, "w").close()  # touch

            fname = os.path.join(versiondir, ".metadata.json")

            with open(fname, "w") as f:
                json.dump({
                    "schema": "pyblish-starter:version-1.0",
                    "version": pyblish_starter.parse_version(version),
                    "path": versiondir,
                    "representations": [
                        {
                            "format": ".ma",
                            "source": os.path.join(
                                "{project}",
                                "maya",
                                "scenes",
                                "scene.ma"
                            ),
                            "path": os.path.join(
                                "{dirname}",
                                "%s{format}" % asset
                            ),
                        },
                    ]
                }, f)


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

    asset = next(pyblish_starter.ls())
    reference = {
        "schema": "pyblish-starter:asset-1.0",
        "name": "Asset1",
        "versions": [
            {
                "schema": "pyblish-starter:version-1.0",
                "version": 1,
                "path": os.path.join(
                    self.tempdir,
                    "shared",
                    "Asset1",
                    "v001"
                ),
                "representations": [
                    {
                        "format": ".ma",
                        "path": os.path.join(
                            "{dirname}",
                            "Asset1{format}"
                        ),
                        "source": os.path.join(
                            "{project}",
                            "maya",
                            "scenes",
                            "scene.ma"
                        )
                    }
                ]
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
    assert False


def test_ls_no_shareddir():
    """A root without /shared returns an empty generator"""

    no_shared = os.path.join(self.tempdir, "noshared")
    os.makedirs(no_shared)

    with root(no_shared):
        assert next(pyblish_starter.ls(), None) is None
