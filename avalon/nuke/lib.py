import os
import contextlib
import nuke
import re
import logging
from ..vendor import (six, clique)

log = logging.getLogger(__name__)


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context

    Example:
        >>> with maintained_selection():
        ...     node['selected'].setValue(True)
        >>> print(node['selected'].value())
        False
    """
    nodes = nuke.allNodes()
    previous_selection = nuke.selectedNodes()

    # deselect all nodes
    reset_selection()

    try:
        # do the operation
        yield
    finally:
        # unselect all selection in case there is some
        reset_selection()
        # and select all previously selected nodes
        if previous_selection:
            try:
                for n in nodes:
                    if n not in previous_selection:
                        continue
                    n['selected'].setValue(True)
            except ValueError as e:
                log.warning(e)


def reset_selection():
    """Deselect all selected nodes
    """
    for node in nuke.selectedNodes():
        node['selected'] = False


def select_nodes(nodes):
    """Selects all inputed nodes

    Arguments:
        nodes (list): nuke nodes to be selected
    """
    assert isinstance(nodes, (list, tuple)), "nodes has to be list or tuple"

    for node in nodes:
        node['selected'].setValue(True)


def add_publish_knob(node):
    """Add Publish knob to node

    Arguments:
        node (obj): nuke node to be processed

    Returns:
        node (obj): processed nuke node
    """
    if "publish" not in node.knobs():
        divider = nuke.Text_Knob('')
        knob = nuke.Boolean_Knob("publish", "Publish", True)
        knob.setFlag(0x1000)
        node.addKnob(divider)
        node.addKnob(knob)
    return node


def set_avalon_knob_data(node, data={}, prefix="ak:"):
    """ Sets a data into nodes's avalon knob

    Arguments:
        node (obj): Nuke node to imprint with data,
        data ( dict): Data to be imprinted into AvalonTab
        prefix (str, optional): filtering prefix

    Returns:
        node (obj)

    Examples:
        data = {
            'asset': 'sq020sh0280',
            'family': 'render',
            'subset': 'subsetMain'
        }
    """
    # fix prefix back compatibility
    if not isinstance(prefix, list):
        prefix = [prefix]

    # definition of knobs
    knobs = [
        {"name": 'AvalonTab', "value": '', "type": "Tab_Knob"},
        {"name": 'begin', "value": 'Avalon data group',
         "type": "Tab_Knob", "group": 2},
        {"name": '__divider__'},
        {"name": 'avalon_data',
         "value": 'Warning! Do not change following data!',
         "type": "Text_Knob"},
        {"name": 'end', "value": 'Avalon data group',
            "type": "Tab_Knob", "group": -1}
    ]
    visible = ["asset", "subset", "name", "namespace"]

    try:
        # create Avalon Tab and basic knobs
        for k in knobs[:-1]:
            if k["name"] in node.knobs().keys():
                continue

            if "__divider__" in k["name"]:
                knob = nuke.Text_Knob("__divider__", "")
                node.addKnob(knob)
                continue

            if not k.get("group"):
                n_knob = getattr(nuke, k["type"])
                knob = n_knob(k["name"])
                node.addKnob(knob)

                try:
                    knob.setValue(k['value'])
                except TypeError as E:
                    log.info("{} - Not correct knob value. Error: `{}`".format(__name__, E))
            else:
                if k["name"] not in node.knobs().keys():
                    n_knob = getattr(nuke, k["type"])
                    knob = n_knob(k["name"], k["value"], k.get("group"))
                    node.addKnob(knob)

        # add avalon knobs for imprinting data
        for key, value in data.items():
            name = prefix[-1] + key
            value = str(value)

            try:
                knob = node.knob(name)
                log.info("Updating: `{0}` to `{1}`".format(name, value))
                node[name].setValue(value)
            except NameError:
                log.info("Setting: `{0}` to `{1}`".format(name, value))
                n_knob = nuke.String_Knob if key in visible else nuke.Text_Knob
                knob = n_knob(name, key, value)
                node.addKnob(knob)

        # adding closing group knob
        cgk = knobs[-1]
        if cgk["name"] not in node.knobs().keys():
            n_knob = getattr(nuke, cgk["type"])
            knob = n_knob(cgk["name"], cgk["value"], cgk.get("group"))
            node.addKnob(knob)

        return node

    except NameError as e:
        log.warning("Failed to add Avalon data to node: `{}`".format(e))
        return False


def get_avalon_knob_data(node, prefix="ak:"):
    """ Gets a data from nodes's avalon knob

    Arguments:
        node (obj): Nuke node to search for data,
        prefix (str, optional): filtering prefix

    Returns:
        data (dict)
    """
    # check if lists
    if not isinstance(prefix, list):
        prefix = list([prefix])

    data = dict()
    log.debug("___> prefix: `{}`".format(prefix))
    # loop prefix
    for p in prefix:

        try:
            # check if data available on the node
            test = node['avalon_data'].value()
            log.debug("Only testing if data avalable: `{}`".format(test))
        except NameError as e:
            # if it doesn't then create it
            log.debug("Creating avalon knob: `{}`".format(e))
            node = set_avalon_knob_data(node)
            return get_avalon_knob_data(node)

        # get data from filtered knobs
        data.update({k.replace(p, ''): node[k].value()
                    for k in node.knobs().keys()
                    if p in k})

    return data

def check_subsetname_exists(nodes, subset_name):
    """
    Checking if node is not already created to secure there is no duplicity

    Arguments:
        nodes (list): list of nuke.Node objects
        subset_name (str): name we try to find

    Returns:
        bool: True of False
    """
    return next((True for n in nodes
    if subset_name in get_avalon_knob_data(n,
        ["avalon:", "ak:"]).get("subset", "")), False)

def imprint(node, data):
    """Adding `Avalon data` into a node's Avalon Tab/Avalon knob
    also including publish knob

    Arguments:
        node (obj): A nuke's node object
        data (dict): Any data which needst to be imprinted

    Returns:
        node (obj)

    Examples:
        data = {
            'asset': 'sq020sh0280',
            'family': 'render',
            'subset': 'subsetMain'
        }
    """
    return add_publish_knob(
        set_avalon_knob_data(node, data)
    )


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
        padding = '#' * len(padding)
        tail = collections[0].format("{tail}")
        file = head + padding + tail

        return {'path': os.path.join(dir, file).replace('\\', '/'),
                'frames': collections[0].format("[{ranges}]")}
    else:
        return False


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
