import os
import re

from maya import cmds

from ..pipeline import (
    register_default,
    register_family,
    _defaults,
    _families,
)


def setup():
    register_default({
        "key": "id",
        "value": "pyblish.starter.instance"
    })

    register_default({"key": "label", "value": "{name}"})
    register_default({"key": "family", "value": "{family}"})

    register_family({
        "name": "starter.model",
        "help": "Polygonal geometry for animation"
    })

    register_family({
        "name": "starter.rig",
        "help": "Character rig"
    })

    register_family({
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

    nodes = cmds.file(fname,
                      namespace=namespace,
                      reference=True)

    return cmds.referenceQuery(nodes, referenceNode=True)


def create(name, family, use_selection=False):
    """Create new instance

    Arguments:
        family (str): Name of family
        use_selection (bool): Use selection to create this instance?

    """

    try:
        item = next(i for i in _families if i["name"] == family)
    except:
        raise RuntimeError("{0} is not a valid family".format(family))

    attrs = _defaults + item.get("attributes", [])

    if not use_selection:
        cmds.select(deselect=True)

    instance = "%s_instance" % name

    if cmds.objExists(instance):
        raise NameError("\"%s\" already exists." % instance)

    instance = cmds.sets(name=instance)

    for item in attrs:
        key = item["key"]

        try:
            value = item["value"].format(
                name=name,
                family=family
            )
        except KeyError as e:
            raise KeyError("Invalid dynamic property: %s" % e)

        if isinstance(value, bool):
            add_type = {"attributeType": "bool"}
            set_type = {"keyable": False, "channelBox": True}
        elif isinstance(value, basestring):
            add_type = {"dataType": "string"}
            set_type = {"type": "string"}
        elif isinstance(value, int):
            add_type = {"attributeType": "long"}
            set_type = {"keyable": False, "channelBox": True}
        elif isinstance(value, float):
            add_type = {"attributeType": "double"}
            set_type = {"keyable": False, "channelBox": True}
        else:
            raise TypeError("Unsupported type: %r" % type(value))

        cmds.addAttr(instance, ln=key, **add_type)
        cmds.setAttr(instance + "." + key, value, **set_type)

    cmds.select(instance, noExpand=True)

    return instance
