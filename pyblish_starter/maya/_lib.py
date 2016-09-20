import os

from maya import cmds, mel

from .._pipeline import (
    find_latest_version,
    _registered_data,
    _registered_families,
)


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
                break

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


def loader(asset, version=-1, namespace=None):
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


def creator(name, family, use_selection=False):
    """Create new instance

    Arguments:
        name (str): Name of instance
        family (str): Name of family
        use_selection (bool): Use selection to create this instance?

    """

    try:
        item = next(i for i in _registered_families if i["name"] == family)
    except:
        raise RuntimeError("{0} is not a valid family".format(family))

    data = _registered_data + item.get("data", [])

    if not use_selection:
        cmds.select(deselect=True)

    instance = "%s_instance" % name

    if cmds.objExists(instance):
        raise NameError("\"%s\" already exists." % instance)

    instance = cmds.sets(name=instance)

    for item in data:
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


def export_alembic(nodes, file, frame_range=None, uv_write=True):
    """Wrap native MEL command with limited set of arguments

    Arguments:
        nodes (list): Long names of nodes to cache
        file (str): Absolute path to output destination
        frame_range (tuple, optional): Start- and end-frame of cache,
            default to current animation range.
        uv_write (bool, optional): Whether or not to include UVs,
            default to True

    """

    options = [
        ("file", file),
        ("frameRange", "%s %s" % frame_range),
    ] + [("root", mesh) for mesh in nodes]

    if uv_write:
        options.append(("uvWrite", ""))

    if frame_range is None:
        frame_range = (
            cmds.playbackOptions(query=True, ast=True),
            cmds.playbackOptions(query=True, aet=True)
        )

    # Generate MEL command
    mel_args = list()
    for key, value in options:
        mel_args.append("-{0} {1}".format(key, value))

    mel_args_string = " ".join(mel_args)
    mel_cmd = "AbcExport -j \"{0}\"".format(mel_args_string)

    return mel.eval(mel_cmd)
