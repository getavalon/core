"""Compatibility

This module is to ensure the compatibility between Maya, Avalon and Pyblish
is maintained.
"""
import maya.cmds as cmds
import os


def remove_googleapiclient():
    """Check if the compatibility must be maintained

    The Maya 2018 version tries to import the `http` module from
    Maya2018\plug-ins\MASH\scripts\googleapiclient\http.py in stead of the module
    from six.py. This import conflict causes a crash Avalon's publisher.
    This is due to Autodesk adding paths to the PYTHONPATH environment variable
    which contain modules instead of only packages.
    """

    keyword = "googleapiclient"

    # reconstruct python paths
    python_paths = os.environ["PYTHONPATH"].split(os.pathsep)
    paths = [path for path in python_paths if keyword not in path]
    os.environ["PYTHONPATH"] = os.pathsep.join(paths)


def install():
    """Run all compatibility functions"""
    if cmds.about(version=True) == "2018":
        remove_googleapiclient()
