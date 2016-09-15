import os
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


def load(asset, version, namespace=None):
    """Load asset

    Arguments:
        asset (str): Name of asset
        version (int): Version number
        namespace (str, optional): Name of namespace

    Returns:
        Assembly/ies

    """

    assert isinstance(version, int), "Version must be integer"

    asset = os.path.join(
        "public",
        asset,
        "v%03d" % version,
        asset + ".ma"
    )

    cmds.file(asset, reference=True, namespace=namespace)
    reference = cmds.file(asset, query=True, referenceNode=True)
    nodes = cmds.referenceQuery(reference, nodes=True)
    return cmds.ls(nodes, assemblies=True)
