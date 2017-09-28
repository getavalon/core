"""Compatibility issues six.py / Maya2018

The Maya 2018 version tries to import the `http` module from
Maya2018\plug-ins\MASH\scripts\googleapiclient\http.py in stead of the module
from six.py. This import conflict causes a crash Avalon's publisher.
This is due to Autodesk adding paths to the PYTHONPATH environment variable
which contain modules instead of only packages.

This will be used until Autodesk has fixed the issue
"""


def check_compatibility():
    """Check if the compatibility must be maintained

    The compatibility will only be maintained when the Maya version is 2018
    """

    import os
    import maya.cmds as cmds

    if cmds.about(verison=True) == "2018":
        keyword = "googleapiclient"

        # reconstruct python paths
        python_paths = os.environ["PYTHONPATH"].split(os.pathsep)
        paths = [path for path in python_paths if keyword not in path]
        os.environ["PYTHONPATH"] = os.pathsep.join(paths)
