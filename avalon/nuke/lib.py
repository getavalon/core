import os
import contextlib
import nuke
import re
import logging
from collections import OrderedDict

from .. import io
from ..vendor import six, clique
from .vendor import knobby

log = logging.getLogger(__name__)


Knobby = knobby.util.Knobby
imprint = knobby.util.imprint
read = knobby.util.read
mold = knobby.util.mold

AVALON_TAB = "avalon"


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context

    Example:
        >>> with maintained_selection():
        ...     node['selected'].setValue(True)
        >>> print(node['selected'].value())
        False
    """
    previous_selection = nuke.selectedNodes()
    try:
        yield
    finally:
        # unselect all selection in case there is some
        current_seletion = nuke.selectedNodes()
        [n['selected'].setValue(False) for n in current_seletion]
        # and select all previously selected nodes
        if previous_selection:
            [n['selected'].setValue(True) for n in previous_selection]


def reset_selection():
    """Deselect all selected nodes
    """
    for node in nuke.selectedNodes():
        node["selected"].setValue(False)


def select_nodes(nodes):
    """Selects all inputed nodes

    Arguments:
        nodes (list): nuke nodes to be selected
    """
    assert isinstance(nodes, (list, tuple)), "nodes has to be list or tuple"

    for node in nodes:
        node["selected"].setValue(True)


def lsattr(attr, value=None, type=None, group=None, recursive=False):
    """Return nodes matching `key` and `value`

    Arguments:
        attr (str): Name of Node knob
        value (object, optional): Value of attribute. If none
            is provided, return all nodes with this attribute.
        type (str, optional): Node class name (Not work with `recursive`)
        group (nuke.Node, optional): Listing nodes from `group`, default `root`
        recursive (bool, optional): Whether to look into child groups.

    Return:
         list: matching nodes.

    """
    group = group or nuke.toNode("root")

    if value is None:
        args = (type, ) if type else ()
        nodes = nuke.allNodes(*args, group=group, recurseGroups=recursive)
        return [n for n in nodes if n.knob(attr)]
    return lsattrs({attr: value}, type=type, group=group, recursive=recursive)


def lsattrs(attrs, type=None, group=None, recursive=False):
    """Return nodes with the given attribute(s).

    Arguments:
        attrs (dict): Name and value pairs of expected matches
        type (str, optional): Node class name (Not work with `recursive`)
        group (nuke.Node, optional): Listing nodes from `group`, default `root`
        recursive (bool, optional): Whether to look into child groups.

    Return:
         list: matching nodes.

    """
    matches = set()
    args = (type, ) if type else ()
    group = group or nuke.toNode("root")
    nodes = nuke.allNodes(*args, group=group, recurseGroups=recursive)
    for node in nodes:
        for attr in attrs:
            knob = node.knob(attr)
            if not knob:
                continue
            elif knob.getValue() != attrs[attr]:
                continue
            else:
                matches.add(node)
    return list(matches)


def set_id(node, container_id=None):
    """Set 'avalonId' to `node`

    Args:
        node (nuke.Node): Node that id to apply to
        container_id (str, optional): `node` container's id

    """
    data = OrderedDict()
    data["avalonId"] = str(io.ObjectId())
    if container_id:
        data["containerId"] = container_id

    set_avalon_knob_data(node, data)

    return data["avalonId"]


def get_id(node, container_id=False):
    """Get 'avalonId' of `node`

    Args:
        node (nuke.Node): Node that id to apply to
        container_id (bool, optional): Whether change to get `node`
            container's id instead of `node` avalonId. Default False.

    """
    knob = "containerId" if container_id else "avalonId"
    id_knob = node.knobs().get("avalon:" + knob)
    return id_knob.value() if id_knob else None


def find_copies(source, group=None, recursive=True):
    """Return nodes that has same 'avalonId' as `source`

    Args:
        source (nuke.Node): The node to find copies from
        group (nuke.Node, optional): Find copies from `group`, default `root`
        recursive (bool, optional): Whether to look into child groups,
            default True.

    """
    assert isinstance(source, nuke.Node), "`Source` needs to be a nuke node."

    copies = list()
    source_id = get_id(source)
    if source_id:
        copies = lsattrs({"avalon:avalonId": source_id},
                         # (NOTE) Cannot specify node `type` to `lsattrs()` if
                         #        `recursive=True`. Because the arg `filter`
                         #        in command `nuke.allNodes` doesn't work with
                         #        `recurseGroups=True`.
                         group=group,
                         recursive=recursive)

    # Dont return the source.
    if source in copies:
        copies.remove(source)

    return copies


@contextlib.contextmanager
def sync_copies(nodes, force=False):
    """Context manager for Syncing nodes' knobs

    When updating subset by `Loader.update`, use this context to auto sync all
    copies of the subset.

    By default, only knobs that haven't been modified, compares to the original
    one inside the "AVALON_CONTAINERS". But if `force` set to True, all knobs
    will be updated.

    Example:
        ```
        class Loader(avalon.api.Loader):

            def update(self, container, representation):

                with lib.sync_copies(nodes):
                    # Update subset
                    ...
                # All copies of `nodes` updated

                with lib.sync_copies([container_node], force=True):
                    # Update container data
                    ...
                # All copies of `container_node` updated

        ```

    Args:
        nodes (list): Nodes to sync
        force (bool, optional): Whether to force updating all knobs

    """
    def is_knob_eq(knob_a, knob_b):
        return knob_a.toScript() == knob_b.toScript()

    def sync_knob(knob_a, knob_b):
        script = knob_a.toScript()
        knob_b.fromScript(script)

    staged = dict()
    origin = dict()

    # Collect knobs for updating
    for node in nodes:
        targets = list()

        sources = node.knobs()
        origin[node] = sources

        for copy in find_copies(node):
            for name, knob in copy.knobs().items():
                if name not in sources:
                    continue
                # Only update knob that hasn't been modified
                if force or is_knob_eq(sources[name], knob):
                    targets.append(knob.fullyQualifiedName())

        if targets:
            staged[node] = targets

    try:
        yield  # Update `nodes`

    finally:
        # Sync update result to all copies
        for node, targets in staged.items():
            updates = origin[node]

            for knob in targets:
                copied, knob = knob.rsplit(".", 1)
                copied = nuke.toNode(copied)

                sync_knob(updates[knob], copied[knob])


def add_publish_knob(node):
    """Add Publish knob to node

    Arguments:
        node (nuke.Node): nuke node to be processed

    Returns:
        node (nuke.Node): processed nuke node

    """
    if "publish" not in node.knobs():
        body = OrderedDict()
        body[("divd", "")] = Knobby("Text_Knob", "")
        body["publish"] = True
        imprint(node, body, tab=AVALON_TAB)
    return node


def set_avalon_knob_data(node, data=None):
    """ Sets data into nodes's avalon knob

    Arguments:
        node (nuke.Node): Nuke node to imprint with data,
        data (dict, optional): Data to be imprinted into AvalonTab
        prefix (str, optional): filtering prefix

    Returns:
        node (nuke.Node)

    Examples:
        data = {
            'asset': 'sq020sh0280',
            'family': 'render',
            'subset': 'subsetMain'
        }
    """
    data = data or dict()

    warn = Knobby("Text_Knob", "Warning! Do not change following data!")
    divd = Knobby("Text_Knob", "")
    knobs = OrderedDict([
        (("warn", ""), warn),
        (("divd", ""), divd),
    ])

    editable = ["asset", "subset", "name", "namespace"]

    for key, value in data.items():
        if key in editable:
            knobs[key] = value
        else:
            knobs[key] = Knobby("String_Knob",
                                str(value),
                                flags=[nuke.READ_ONLY])

    imprint(node, knobs, tab=AVALON_TAB)

    return node


def get_avalon_knob_data(node):
    """ Get data from nodes's avalon knob

    Arguments:
        node (nuke.Node): Nuke node to search for data,
        prefix (str, optional): filtering prefix

    Returns:
        data (dict)
    """
    def compat_prefixed(knob_name):
        if knob_name.startswith("avalon:"):
            return knob_name[len("avalon:"):]
        elif knob_name.startswith("ak:"):
            return knob_name[len("ak:"):]
        else:
            return None

    return read(node, filter=compat_prefixed)


def fix_data_for_node_create(data):
    """Fixing data to be used for nuke knobs
    """
    for k, v in data.items():
        if isinstance(v, six.text_type):
            data[k] = str(v)
        if str(v).startswith("0x"):
            data[k] = int(v, 16)
    return data


def add_write_node(name, **kwarg):
    """Adding nuke write node

    Arguments:
        name (str): nuke node name
        kwarg (attrs): data for nuke knobs

    Returns:
        node (obj): nuke write node
    """
    frame_range = kwarg.get("frame_range", None)

    w = nuke.createNode(
        "Write",
        "name {}".format(name))

    w["file"].setValue(kwarg["file"])

    for k, v in kwarg.items():
        if "frame_range" in k:
            continue
        log.info([k, v])
        try:
            w[k].setValue(v)
        except KeyError as e:
            log.debug(e)
            continue

    if frame_range:
        w["use_limit"].setValue(True)
        w["first"].setValue(frame_range[0])
        w["last"].setValue(frame_range[1])

    return w


def get_node_path(path, padding=4):
    """Get filename for the Nuke write with padded number as '#'

    Arguments:
        path (str): The path to render to.

    Returns:
        tuple: head, padding, tail (extension)

    Examples:
        >>> get_frame_path("test.exr")
        ('test', 4, '.exr')

        >>> get_frame_path("filename.#####.tif")
        ('filename.', 5, '.tif')

        >>> get_frame_path("foobar##.tif")
        ('foobar', 2, '.tif')

        >>> get_frame_path("foobar_%08d.tif")
        ('foobar_', 8, '.tif')
    """
    filename, ext = os.path.splitext(path)

    # Find a final number group
    if '%' in filename:
        match = re.match('.*?(%[0-9]+d)$', filename)
        if match:
            padding = int(match.group(1).replace('%', '').replace('d', ''))
            # remove number from end since fusion
            # will swap it with the frame number
            filename = filename.replace(match.group(1), '')
    elif '#' in filename:
        match = re.match('.*?(#+)$', filename)

        if match:
            padding = len(match.group(1))
            # remove number from end since fusion
            # will swap it with the frame number
            filename = filename.replace(match.group(1), '')

    return filename, padding, ext


def ls_img_sequence(path):
    """Listing all available coherent image sequence from path

    Arguments:
        path (str): A nuke's node object

    Returns:
        data (dict): with nuke formated path and frameranges
    """
    file = os.path.basename(path)
    dir = os.path.dirname(path)
    base, ext = os.path.splitext(file)
    name, padding = os.path.splitext(base)

    # populate list of files
    files = [f for f in os.listdir(dir)
             if name in f
             if ext in f]

    # create collection from list of files
    collections, reminder = clique.assemble(files)

    if len(collections) > 0:
        head = collections[0].format("{head}")
        padding = collections[0].format("{padding}") % 1
        padding = "#" * len(padding)
        tail = collections[0].format("{tail}")
        file = head + padding + tail

        return {"path": os.path.join(dir, file).replace("\\", "/"),
                "frames": collections[0].format("[{ranges}]")}
    else:
        return False
