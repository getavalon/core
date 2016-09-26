"""Standalone helper functions"""

from maya import cmds, mel


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
