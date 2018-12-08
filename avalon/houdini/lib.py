import contextlib

import hou
from ..vendor import six


def children_as_string(node):
    return [c.name() for c in node.children()]


def imprint(node, data):
    """Store attributes with value on a node

    Depending on the type of attribute it creates the correct parameter
    template. Houdini uses a template per type, see the docs for more
    information.

    http://www.sidefx.com/docs/houdini/hom/hou/ParmTemplate.html

    Args:
        node(hou.Node): node object from Houdini
        data(dict): collection of attributes and their value

    Returns:
        None

    """

    parm_group = node.parmTemplateGroup()

    parm_folder = hou.FolderParmTemplate("folder", "Extra")
    for key, value in data.items():
        if value is None:
            continue

        if isinstance(value, float):
            parm = hou.FloatParmTemplate(name=key,
                                         label=key,
                                         num_components=1,
                                         default_value=(value,))
        elif isinstance(value, bool):
            parm = hou.ToggleParmTemplate(name=key,
                                          label=key,
                                          default_value=value)
        elif isinstance(value, int):
            parm = hou.IntParmTemplate(name=key,
                                       label=key,
                                       num_components=1,
                                       default_value=(value,))
        elif isinstance(value, six.string_types):
            parm = hou.StringParmTemplate(name=key,
                                          label=key,
                                          num_components=1,
                                          default_value=(value,))
        else:
            raise TypeError("Unsupported type: %r" % type(value))

        parm_folder.addParmTemplate(parm)

    parm_group.append(parm_folder)
    node.setParmTemplateGroup(parm_group)


def lsattr(attr, value=None):
    nodes = list(hou.node("/obj").allNodes())
    if value is None:
        return [n for n in nodes if n.parm(attr)]
    return lsattrs({attr: value})


def lsattrs(attrs):
    """Return nodes matching `key` and `value`

    Arguments:
        attrs (dict): collection of attribute: value

    Example:
        >> lsattrs({"id": "myId"})
        ["myNode"]
        >> lsattr("id")
        ["myNode", "myOtherNode"]

    Returns:
        list
    """

    matches = set()
    nodes = list(hou.node("/obj").allNodes())  # returns generator object
    for node in nodes:
        for attr in attrs:
            if not node.parm(attr):
                continue
            elif node.evalParm(attr) != attrs[attr]:
                continue
            else:
                matches.add(node)

    return list(matches)


def read(node):
    """Read the container data in to a dict

    Args:
        node(hou.Node): Houdini node

    Returns:
        dict

    """
    # `spareParms` returns a tuple of hou.Parm objects
    return {parameter.name(): parameter.eval() for
            parameter in node.spareParms()}


def unique_name(name, format="%03d", namespace="", prefix="", suffix="",
                separator="_"):
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
        >>> name = hou.node("/obj").createNode("geo", name="MyName")
        >>> assert hou.node("/obj/MyName")
        True
        >>> unique = unique_name(name)
        >>> assert hou.node("/obj/{}".format(unique))
        False

    """

    iteration = 1

    parts = [prefix, name, format % iteration, suffix]
    if namespace:
        parts.insert(0, namespace)

    unique = separator.join(parts)
    children = children_as_string(hou.node("/obj"))
    while unique in children:
        iteration += 1
        unique = separator.join(parts)

    if suffix:
        return unique[:-len(suffix)]

    return unique


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context
    Example:
        >>> with maintained_selection():
        ...     # Modify selection
        ...     node.setSelected(on=False, clear_all_selected=True)
        >>> # Selection restored
    """

    previous_selection = hou.selectedNodes()
    try:
        yield
    finally:
        # Clear the selection
        # todo: does hou.clearAllSelected() do the same?
        for node in hou.selectedNodes():
            node.setSelected(on=False)

        if previous_selection:
            for node in previous_selection:
                node.setSelected(on=True)
