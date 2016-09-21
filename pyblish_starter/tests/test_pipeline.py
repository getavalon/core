import os
import sys
import shutil
import tempfile

import pyblish_starter

self = sys.modules[__name__]


def setup():
    self.tempdir = tempfile.mkdtemp()
    sys.stdout.write("Created temporary directory \"%s\"" % self.tempdir)


def teardown():
    shutil.rmtree(self.tempdir)
    sys.stdout.write("Removed temporary directory \"%s\"" % self.tempdir)


def test_ls():
    """ls() returns available assets from current root directory"""
    root = os.path.join(
        self.tempdir,
        "public"
    )
    
    for asset in ("Asset1", "Asset2"):
        os.makedirs(os.path.join(root, asset))
    
    pyblish_starter.register_root(self.tempdir)
    
    assert pyblish_starter.ls() == ["Asset1", "Asset2"]
