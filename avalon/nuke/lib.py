import os
import contextlib
import nuke
import re
import logging
from ..vendor import clique

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
    try:
        yield
    finally:
        # unselect all selection in case there is some
        [n['selected'].setValue(False) for n in nodes]
        # and select all previously selected nodes
        if previous_selection:
            [n['selected'].setValue(True)
             for n in nodes
             if n.name() in previous_selection]


def reset_selection():
    """Deselect all selected nodes
    """
    nodes = nuke.allNodes()
    [n['selected'].setValue(False) for n in nodes]


def select_nodes(nodes):
    """Selects all inputed nodes

    Arguments:
        nodes (list): nuke nodes to be selected
    """
    assert isinstance(nodes, (list, tuple)), "nodes has to be list or tuple"

    [n['selected'].setValue(True) for n in nodes]


def add_publish_knob(node):
    '''Adds Publish node to node

    Arguments:
        node (obj): nuke node to be processed

    Returns:
        node (obj): processed nuke node
    '''
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
    knobs = [
        {"name": 'AvalonTab', "value": '', "type": "Tab_Knob"},
        {"name": 'begin', "value": 'Avalon data group',
         "type": "Tab_Knob", "group": 2},
        {"name": '__divider__'},
        {"name": 'avalon_data',
         "value": 'Warning! Do not change following data!',
         "type": "Text_Knob"},
        {"name": '__divider__'},
        {"name": 'begin',
         "value": 'Avalon data group',
         "type": "Tab_Knob", "group": -1}
    ]
    non_hiden = ["asset", "subset", "name", "namespace"]

    try:
        # create Avalon Tab and basic knobs
        for k in knobs[:-1]:
            if not k.get("group"):
                if "__divider__" in k["name"]:
                    knob = nuke.Text_Knob("")
                    node.addKnob(knob)
                elif k["name"] not in node.knobs().keys():
                    knob = eval("nuke.{type}('{name}')".format(**k))
                    node.addKnob(knob)
                    try:
                        knob.setValue(k['value'])
                    except TypeError as E:
                        print(E)
            else:
                if k["name"] not in node.knobs().keys():
                    knob = eval(
                        "nuke.{type}('{name}', '{value}', {group})".format(**k))
                    node.addKnob(knob)

        # add avalon knobs for imprinting data
        for k, v in data.items():
            label = k
            name = prefix + label
            value = str(v)
            if label in non_hiden:
                if name not in node.knobs().keys():
                    log.info("Setting: `{0}` to `{1}`".format(name, value))
                    knob = eval(
                        "nuke.String_Knob('{name}','{label}','{value}')".format(
                            name=name,
                            label=label,
                            value=value
                        ))
                    node.addKnob(knob)
                else:
                    log.info("Updating: `{0}` to `{1}`".format(name, value))
                    node[name].setValue(value)
            else:
                if name not in node.knobs().keys():
                    log.info("Setting: `{0}` to `{1}`".format(name, value))
                    knob = eval(
                        "nuke.Text_Knob('{name}','{label}','{value}')".format(
                            name=name,
                            label=label,
                            value=value
                            ))
                    node.addKnob(knob)
                else:
                    log.info("Updating: `{0}` to `{1}`".format(name, value))
                    node[name].setValue(str(value))

        # adding closing group knob
        knob = eval(
            "nuke.{type}('{name}', '{value}', {group})".format(**knobs[-1]))
        node.addKnob(knob)

        return node

    except Exception as e:
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
    try:
        # check if data available on the node
        test = node['avalon_data'].value()
        log.debug("Only testing if data avalable: `{}`".format(test))
    except Exception as e:
        # if it doesn't then create it
        log.debug("Creating avalon knob: `{}`".format(e))
        node = set_avalon_knob_data(node)
        return get_avalon_knob_data(node)

    # get data from filtered knobs
    data = {k.replace(prefix, ''): node[k].value()
            for k in node.knobs().keys()
            if prefix in k}

    return data


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
    node = set_avalon_knob_data(node, data)
    node = add_publish_knob(node)

    return node


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
        try:
            if isinstance(v, unicode):
                data[k] = str(v)
        except Exception:
            data[k] = str(v)

        if "0x" in str(v):
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
