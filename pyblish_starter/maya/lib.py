import os
import re
from maya import cmds


def setup():
    from ..tools import instance_creator

    instance_creator.register_default({
        "key": "id",
        "value": "pyblish.starter.instance"
    })

    instance_creator.register_default({"key": "label", "value": "{name}"})
    instance_creator.register_default({"key": "family", "value": "{family}"})

    instance_creator.register_family({
        "name": "starter.model",
        "help": "Polygonal geometry for animation"
    })

    instance_creator.register_family({
        "name": "starter.rig",
        "help": "Character rig"
    })

    instance_creator.register_family({
        "name": "starter.animation",
        "help": "Pointcache"
    })


def hierarchy_from_string(hierarchy):
    parents = {}

    for line in hierarchy.split("\n"):
        if not line:
            continue

        name = line.strip()
        padding = len(line[:-len(name)])
        parents[padding] = name

        name = cmds.createNode("transform", name=name)

        for parent in sorted(parents):
            if parent < padding:
                cmds.parent(name, parents[parent])

    # Return assembly
    return parents[0]


def outmesh(shape, name=None):
    """Construct a new shape with a connection to source.inMesh

    Arguments:
        shape (str): Long name of source shape
        name (str, optional): Default "outMesh1"

    Returns:
        transform of new shape

    """

    outmesh = cmds.createNode("mesh")
    cmds.connectAttr(shape + ".outMesh", outmesh + ".inMesh")
    outmesh = cmds.listRelatives(outmesh, parent=True)[0]
    outmesh = cmds.rename(outmesh, name or "outMesh1")
    cmds.sets(outmesh, addElement="initialShadingGroup")
    return outmesh


def find_latest_version(versions):
    """Return latest version from list of versions

    If multiple numbers are found in a single version,
    the last one found is used. E.g. (6) from "v7_22_6"

    Arguments:
        versions (list): Version numbers as string

    Example:
        >>> find_next_version(["v001", "v002", "v003"])
        4
        >>> find_next_version(["1", "2", "3"])
        4
        >>> find_next_version(["v1", "v0002", "verision_3"])
        4
        >>> find_next_version(["v2", "5_version", "verision_8"])
        9
        >>> find_next_version(["v2", "v3_5", "_1_2_3", "7, 4"])
        6
        >>> find_next_version(["v010", "v011"])
        12

    """

    highest_version = 0
    for version in versions:
        matches = re.findall(r"\d+", version)

        if not matches:
            continue

        version = int(matches[-1])
        if version > highest_version:
            highest_version = version

    return highest_version


def find_next_version(versions):
    return find_latest_version(versions) + 1


def load(asset, version=-1, namespace=None):
    """Load asset

    Arguments:
        asset (str): Name of asset
        version (int, optional): Version number, defaults to latest
        namespace (str, optional): Name of namespace

    Returns:
        Reference node

    """

    assert isinstance(version, int), "Version must be integer"

    dirname = os.path.join(
        cmds.workspace(rootDirectory=True, query=True),
        "public",
        asset
    )

    try:
        versions = os.listdir(dirname)
    except OSError:
        raise OSError("\"%s\" not found." % asset)

    if version == -1:
        version = find_latest_version(versions)

    fname = os.path.join(
        dirname,
        "v%03d" % version,
        asset + ".ma"
    )

    return cmds.file(fname,
                     namespace=namespace,
                     reference=True,
                     referenceNode=True)
