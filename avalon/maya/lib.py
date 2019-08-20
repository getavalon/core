"""Standalone helper functions"""

import contextlib

from maya import cmds, mel
from maya.api import OpenMaya as om


def unique_name(name, format="%02d", namespace="", prefix="", suffix=""):
    """Return unique `name`

    The function takes into consideration an optional `namespace`
    and `suffix`. The suffix is included in evaluating whether a
    name exists - such as `name` + "_GRP" - but isn't included
    in the returned value.

    If a namespace is provided, only names within that namespace
    are considered when evaluating whether the name is unique.

    Arguments:
        format (str, optional): The `name` is given a number, this determines
            how this number is formatted. Defaults to a padding of 2.
            E.g. my_name01, my_name02.
        namespace (str, optional): Only consider names within this namespace.
        suffix (str, optional): Only consider names with this suffix.

    Example:
        >>> name = cmds.createNode("transform", name="MyName")
        >>> cmds.objExists(name)
        True
        >>> unique = unique_name(name)
        >>> cmds.objExists(unique)
        False

    """

    iteration = 1
    unique = prefix + (name + format % iteration) + suffix

    while cmds.objExists(namespace + ":" + unique):
        iteration += 1
        unique = prefix + (name + format % iteration) + suffix

    if suffix:
        return unique[:-len(suffix)]

    return unique


def unique_namespace(namespace, format="%02d", prefix="", suffix=""):
    """Return unique namespace

    Similar to :func:`unique_name` but evaluating namespaces
    as opposed to object names.

    Arguments:
        namespace (str): Name of namespace to consider
        format (str, optional): Formatting of the given iteration number
        suffix (str, optional): Only consider namespaces with this suffix.

    """

    iteration = 1
    unique = prefix + (namespace + format % iteration) + suffix

    # The `existing` set does not just contain the namespaces but *all* nodes
    # within "current namespace". We need all because the namespace could
    # also clash with a node name. To be truly unique and valid one needs to
    # check against all.
    existing = set(cmds.namespaceInfo(listNamespace=True))
    while unique in existing:
        iteration += 1
        unique = prefix + (namespace + format % iteration) + suffix

    return unique


def read(node):
    """Return user-defined attributes from `node`"""

    data = dict()

    for attr in cmds.listAttr(node, userDefined=True) or list():
        try:
            value = cmds.getAttr(node + "." + attr, asString=True)

        except RuntimeError:
            # For Message type attribute or others that have connections,
            # take source node name as value.
            source = cmds.listConnections(node + "." + attr,
                                          source=True,
                                          destination=False)
            source = cmds.ls(source, long=True) or [None]
            value = source[0]

        except ValueError:
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
                   write_uv=True,
                   write_visibility=True,
                   attribute_prefix=None):
    """Wrap native MEL command with limited set of arguments

    Arguments:
        nodes (list): Long names of nodes to cache

        file (str): Absolute path to output destination

        frame_range (tuple, optional): Start- and end-frame of cache,
            default to current animation range.

        write_uv (bool, optional): Whether or not to include UVs,
            default to True

        write_visibility (bool, optional): Turn on to store the visibility
        state of objects in the Alembic file. Otherwise, all objects are
        considered visible, default to True

        attribute_prefix (str, optional): Include all user-defined
            attributes with this prefix.

    """

    if frame_range is None:
        frame_range = (
            cmds.playbackOptions(query=True, ast=True),
            cmds.playbackOptions(query=True, aet=True)
        )

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

    if write_uv:
        options.append(("uvWrite", ""))

    if write_visibility:
        options.append(("writeVisibility", ""))

    # Generate MEL command
    mel_args = list()
    for key, value in options:
        mel_args.append("-{0} {1}".format(key, value))

    mel_args_string = " ".join(mel_args)
    mel_cmd = "AbcExport -j \"{0}\"".format(mel_args_string)

    # For debuggability, put the string passed to MEL in the Script editor.
    print("mel.eval('%s')" % mel_cmd)

    return mel.eval(mel_cmd)


@contextlib.contextmanager
def undo_chunk():
    """Open a undo chunk during context."""

    try:
        cmds.undoInfo(openChunk=True)
        yield
    finally:
        cmds.undoInfo(closeChunk=True)


def imprint(node, data):
    """Write `data` to `node` as userDefined attributes

    Arguments:
        node (str): Long name of node
        data (dict): Dictionary of key/value pairs

    Example:
        >>> from maya import cmds
        >>> def compute():
        ...   return 6
        ...
        >>> cube, generator = cmds.polyCube()
        >>> imprint(cube, {
        ...   "regularString": "myFamily",
        ...   "computedValue": lambda: compute()
        ... })
        ...
        >>> cmds.getAttr(cube + ".computedValue")
        6

    """

    for key, value in data.items():

        if callable(value):
            # Support values evaluated at imprint
            value = value()

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
        elif isinstance(value, (list, tuple)):
            add_type = {"attributeType": "enum", "enumName": ":".join(value)}
            set_type = {"keyable": False, "channelBox": True}
            value = 0  # enum default
        else:
            raise TypeError("Unsupported type: %r" % type(value))

        cmds.addAttr(node, longName=key, **add_type)
        cmds.setAttr(node + "." + key, value, **set_type)


@contextlib.contextmanager
def without_extension():
    """Use cmds.file with defaultExtensions=False"""
    previous_setting = cmds.file(defaultExtensions=True, query=True)
    try:
        cmds.file(defaultExtensions=False)
        yield
    finally:
        cmds.file(defaultExtensions=previous_setting)


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context

    Example:
        >>> scene = cmds.file(new=True, force=True)
        >>> node = cmds.createNode("transform", name="Test")
        >>> cmds.select("persp")
        >>> with maintained_selection():
        ...     cmds.select("Test", replace=True)
        >>> "Test" in cmds.ls(selection=True)
        False

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
            cmds.select(clear=True)


@contextlib.contextmanager
def suspended_refresh():
    """Suspend viewport refreshes"""

    try:
        cmds.refresh(suspend=True)
        yield
    finally:
        cmds.refresh(suspend=False)


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

            # Objects in this group are those that haven't got
            # any shaders. These are expected to be managed
            # elsewhere, such as by the default model loader.
            if shader == "initialShadingGroup":
                continue

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
            except KeyError:
                continue

        # Remove duplicates
        shader_by_id[shader] = list(set(shader_by_id[shader]))

    return shader_by_id


def apply_shaders(relationships, namespace=None):
    """Given a dictionary of `relationships`, apply shaders to meshes

    Arguments:
        relationships (avalon-core:shaders-1.0): A dictionary of
            shaders and how they relate to meshes.

    """

    if namespace is not None:
        # Append namespace to shader group identifier.
        # E.g. `blinn1SG` -> `Bruce_:blinn1SG`
        relationships = {
            "%s:%s" % (namespace, shader): relationships[shader]
            for shader in relationships
        }

    for shader, ids in relationships.items():
        print("Looking for '%s'.." % shader)
        shader = next(iter(cmds.ls(shader)), None)
        assert shader, "Associated shader not part of asset, this is a bug"

        for id_ in ids:
            mesh, faces = (id_.rsplit(".", 1) + [""])[:2]

            # Find all meshes matching this particular ID
            # Convert IDs to mesh + id, e.g. "nameOfNode.f[1:100]"
            meshes = list(".".join([mesh, faces])
                          for mesh in lsattr("mbID", value=mesh))

            if not meshes:
                continue

            print("Assigning '%s' to '%s'" % (shader, ", ".join(meshes)))
            cmds.sets(meshes, forceElement=shader)


def lsattr(attr, value=None):
    """Return nodes matching `key` and `value`

    Arguments:
        attr (str): Name of Maya attribute
        value (object, optional): Value of attribute. If none
            is provided, return all nodes with this attribute.

    Example:
        >> lsattr("id", "myId")
        ["myNode"]
        >> lsattr("id")
        ["myNode", "myOtherNode"]

    """

    if value is None:
        return cmds.ls("*.%s" % attr,
                       recursive=True,
                       objectsOnly=True,
                       long=True)
    return lsattrs({attr: value})


def lsattrs(attrs):
    """Return nodes with the given attribute(s).

    Arguments:
        attrs (dict): Name and value pairs of expected matches

    Example:
        >> # Return nodes with an `age` of five.
        >> lsattr({"age": "five"})
        >> # Return nodes with both `age` and `color` of five and blue.
        >> lsattr({"age": "five", "color": "blue"})

    Return:
         list: matching nodes.

    """

    dep_fn = om.MFnDependencyNode()
    dag_fn = om.MFnDagNode()
    selection_list = om.MSelectionList()

    first_attr = attrs.iterkeys().next()

    try:
        selection_list.add("*.{0}".format(first_attr),
                           searchChildNamespaces=True)
    except RuntimeError as exc:
        if str(exc).endswith("Object does not exist"):
            return []

    matches = set()
    for i in range(selection_list.length()):
        node = selection_list.getDependNode(i)
        if node.hasFn(om.MFn.kDagNode):
            fn_node = dag_fn.setObject(node)
            full_path_names = [path.fullPathName()
                               for path in fn_node.getAllPaths()]
        else:
            fn_node = dep_fn.setObject(node)
            full_path_names = [fn_node.name()]

        for attr in attrs:
            try:
                plug = fn_node.findPlug(attr, True)
                if plug.asString() != attrs[attr]:
                    break
            except RuntimeError:
                break
        else:
            matches.update(full_path_names)

    return list(matches)
