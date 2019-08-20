import os
import contextlib
import nuke
import re
import logging
import toml

log = logging.getLogger(__name__)


@contextlib.contextmanager
def maintained_selection():
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


def add_avalon_tab_knob(node):
    """Adding a tab and a knob into a node
    """
    try:
        node['avalon'].value()
    except Exception:
        tab = nuke.Tab_Knob("Avalon")
        uk = nuke.Text_Knob('avalon', 'avalon data')
        node.addKnob(tab)
        node.addKnob(uk)
        log.info("created new user knob avalon")


def imprint(node, data):
    """Adding `Avalon data` into a node's Avalon Tab/Avalon knob
    also including publish knob

    Arguments:
        node (list or obj): A nuke's node object either in list or individual
        data (dict): Any data which needst to be imprinted
    """
    if not node:
        return
    if isinstance(node, list):
        node = node[0]

    add_avalon_tab_knob(node)
    add_publish_knob(node)
    node['avalon'].setValue(toml.dumps(data))

    return node


def add_publish_knob(node):
    if "publish" not in node.knobs():
        knob = nuke.Boolean_Knob("publish", "Publish")
        knob.setFlag(0x1000)
        knob.setValue(False)
        node.addKnob(knob)
    return node


def fix_data_for_node_create(data):
    for k, v in data.items():

        data[k] = str(v)

        if "True" in v:
            data[k] = True
        if "False" in v:
            data[k] = False
        if "0x" in v:
            data[k] = int(v, 16)
    return data


def add_write_node(name, **kwarg):
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

    log.info(w)
    return w


def get_node_path(path, padding=4):
    """Get filename for the Nuke write with padded number as '#'

    >>> get_frame_path("test.exr")
    ('test', 4, '.exr')

    >>> get_frame_path("filename.#####.tif")
    ('filename.', 5, '.tif')

    >>> get_frame_path("foobar##.tif")
    ('foobar', 2, '.tif')

    >>> get_frame_path("foobar_%08d.tif")
    ('foobar_', 8, '.tif')

    Args:
        path (str): The path to render to.

    Returns:
        tuple: head, padding, tail (extension)

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
