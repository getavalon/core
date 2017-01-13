"""Standalone helper functions"""

import contextlib
from maya import cmds, mel


def unique_name(name, format="%02d", namespace="", suffix=""):
    iteration = 1
    unique = (name + format % iteration) + suffix

    while cmds.objExists(namespace + ":" + unique):
        iteration += 1
        unique = (name + format % iteration) + suffix

    return unique[:-len(suffix)] if suffix else unique


def unique_namespace(namespace, format="%02d", suffix=""):
    iteration = 1
    unique = (namespace + format % iteration) + suffix

    while unique in cmds.namespaceInfo(listNamespace=True):
        iteration += 1
        unique = (namespace + format % iteration) + suffix

    return unique


def read(node):
    """Return user-defined attributes from `node`

    """

    data = dict()

    for attr in cmds.listAttr(node, userDefined=True) or list():
        try:
            value = cmds.getAttr(node + "." + attr)
        except:
            # Some attributes cannot be read directly,
            # such as mesh and color attributes. These
            # are considered non-essential to this
            # particular publishing pipeline.
            value = None

        data[attr] = value

    return data


def export_alembic(nodes,
                   file,
                   frame_range=None,
                   uv_write=True,
                   attribute_prefix=None):
    """Wrap native MEL command with limited set of arguments

    Arguments:
        nodes (list): Long names of nodes to cache
        file (str): Absolute path to output destination
        frame_range (tuple, optional): Start- and end-frame of cache,
            default to current animation range.
        uv_write (bool, optional): Whether or not to include UVs,
            default to True
        attribute_prefix (str, optional): Include all user-defined
            attributes with this prefix.

    """

    options = [
        ("file", file),
        ("frameRange", "%s %s" % frame_range),
    ] + [("root", mesh) for mesh in nodes]

    if isinstance(attribute_prefix, basestring):
        # Include all attributes prefixed with "mb"
        # TODO(marcus): This would be a good candidate for
        #   external registration, so that the developer
        #   doesn't have to edit this function to modify
        #   the behavior of Alembic export.
        options.append(("attrPrefix", str(attribute_prefix)))

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

    # For debuggability, put the string passed to MEL in the Script editor.
    print("lib.export_alembic('%s')" % mel_cmd)

    return mel.eval(mel_cmd)


def imprint(node, data):
    """Write `data` to `node` as userDefined attributes

    Arguments:
        node (str): Long name of node
        data (dict): Dictionary of key/value pairs

    """

    for key, value in data.items():
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

        cmds.addAttr(node, longName=key, **add_type)
        cmds.setAttr(node + "." + key, value, **set_type)


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context

    Example:
        >>> with maintained_selection():
        ...     # Modify selection
        ...     cmds.select('node', replace=True)
        >>> # Selection restored

    """

    previous_selection = cmds.ls(selection=True)
    try:
        yield
    finally:
        if previous_selection:
            cmds.select(previous_selection,
                        replace=True,
                        noExpand=True)
        else:
            cmds.select(deselect=True,
                        noExpand=True)


def serialise_shaders(nodes):
    """Generate a shader set dictionary

    Arguments:
        nodes (list): Absolute paths to nodes

    Returns:
        dictionary of (shader: id) pairs

    Schema:
        {
            "shader1": ["id1", "id2"],
            "shader2": ["id3", "id1"]
        }

    Example:
        {
            "Bazooka_Brothers01_:blinn4SG": [
                "f9520572-ac1d-11e6-b39e-3085a99791c9.f[4922:5001]",
                "f9520572-ac1d-11e6-b39e-3085a99791c9.f[4587:4634]",
                "f9520572-ac1d-11e6-b39e-3085a99791c9.f[1120:1567]",
                "f9520572-ac1d-11e6-b39e-3085a99791c9.f[4251:4362]"
            ],
            "lambert2SG": [
                "f9520571-ac1d-11e6-9dbb-3085a99791c9"
            ]
        }

    """

    valid_nodes = cmds.ls(
        nodes,
        long=True,
        recursive=True,
        showType=True,
        objectsOnly=True,
        type="transform"
    )

    meshes_by_id = {}
    for mesh in valid_nodes:
        shapes = cmds.listRelatives(valid_nodes[0],
                                    shapes=True,
                                    fullPath=True) or list()

        if shapes:
            shape = shapes[0]
            if not cmds.nodeType(shape):
                continue

            try:
                id_ = cmds.getAttr(mesh + ".mbID")

                if id_ not in meshes_by_id:
                    meshes_by_id[id_] = list()

                meshes_by_id[id_].append(mesh)

            except ValueError:
                continue

    meshes_by_shader = dict()
    for id_, mesh in meshes_by_id.items():
        shape = cmds.listRelatives(mesh,
                                   shapes=True,
                                   fullPath=True) or list()

        for shader in cmds.listConnections(shape,
                                           type="shadingEngine") or list():

            if shader not in meshes_by_shader:
                meshes_by_shader[shader] = list()

            shaded = cmds.sets(shader, query=True) or list()
            meshes_by_shader[shader].extend(shaded)

    shader_by_id = {}
    for shader, shaded in meshes_by_shader.items():

        if shader not in shader_by_id:
            shader_by_id[shader] = list()

        for mesh in shaded:

            # Enable shader assignment to faces.
            name = mesh.split(".f[")[0]

            transform = name
            if cmds.objectType(transform) == "mesh":
                transform = cmds.listRelatives(name, parent=True)[0]

            try:
                id_ = cmds.getAttr(transform + ".mbID")
                shader_by_id[shader].append(mesh.replace(name, id_))
            except:
                continue

        # Remove duplicates
        shader_by_id[shader] = list(set(shader_by_id[shader]))

    return shader_by_id
