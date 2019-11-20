import os
import contextlib
import nuke
import re
import logging
from collections import OrderedDict

from ..vendor import six

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


def imprint(node, data, tab=None):
    """Store attributes with value on node

    Parse user data into Node knobs.
    Use `collections.OrderedDict` to ensure knob order.

    Args:
        node(nuke.Node): node object from Nuke
        data(dict): collection of attributes and their value

    Returns:
        None

    Examples:
        ```
        import nuke
        from avalon.nuke import lib

        node = nuke.createNode("NoOp")
        data = {
            # Regular type of attributes
            "myList": ["x", "y", "z"],
            "myBool": True,
            "myFloat": 0.1,
            "myInt": 5,

            # Creating non-default imprint type of knob
            "MyFilePath": lib.Knobby("File_Knob", "/file/path"),
            "divider": lib.Knobby("Text_Knob", ""),

            # Manual nice knob naming
            ("my_knob", "Nice Knob Name"): "some text",

            # dict type will be created as knob group
            "KnobGroup": {
                "knob1": 5,
                "knob2": "hello",
                "knob3": ["a", "b"],
            },

            # Nested dict will be created as tab group
            "TabGroup": {
                "tab1": {"count": 5},
                "tab2": {"isGood": True},
                "tab3": {"direction": ["Left", "Right"]},
            },
        }
        lib.imprint(node, data, tab="Demo")

        ```

    """
    for knob in create_knobs(data, tab):
        node.addKnob(knob)


class Knobby(object):
    """For creating knob which it's type isn't mapped in `create_knobs`

    Args:
        type (string): Nuke knob type name
        value: Value to be set with `Knob.setValue`, put `None` if not required
        *args: Args other than knob name for initializing knob class

    """

    def __init__(self, type, value, *args):
        self.type = type
        self.value = value
        self.args = args

    def create(self, name, nice=None):
        knob_cls = getattr(nuke, self.type)
        knob = knob_cls(name, nice, *self.args)
        if self.value is not None:
            knob.setValue(self.value)
        return knob


def create_knobs(data, tab=None):
    """Create knobs by data

    Depending on the type of each dict value and creates the correct Knob.

    Mapped types:
        bool: nuke.Boolean_Knob
        int: nuke.Int_Knob
        float: nuke.Double_Knob
        list: nuke.Enumeration_Knob
        six.string_types: nuke.String_Knob

        dict: If it's a nested dict (all values are dict), will turn into
            A tabs group. Or just a knobs group.

    Args:
        data (dict): collection of attributes and their value
        tab (string, optional): Knobs' tab name

    Returns:
        list: A list of `nuke.Knob` objects

    """
    def nice_naming(key):
        """Convert camelCase name into UI Display Name"""
        words = re.findall('[A-Z][^A-Z]*', key[0].upper() + key[1:])
        return " ".join(words)

    # Turn key-value pairs into knobs
    knobs = list()

    if tab:
        knobs.append(nuke.Tab_Knob(tab))

    for key, value in data.items():
        # Knob name
        if isinstance(key, tuple):
            name, nice = key
        else:
            name, nice = key, nice_naming(key)

        # Create knob by value type
        if isinstance(value, Knobby):
            knobby = value
            knob = knobby.create(name, nice)

        elif isinstance(value, float):
            knob = nuke.Double_Knob(name, nice)
            knob.setValue(value)

        elif isinstance(value, bool):
            knob = nuke.Boolean_Knob(name, nice)
            knob.setValue(value)
            knob.setFlag(nuke.STARTLINE)

        elif isinstance(value, int):
            knob = nuke.Int_Knob(name, nice)
            knob.setValue(value)

        elif isinstance(value, six.string_types):
            knob = nuke.String_Knob(name, nice)
            knob.setValue(value)

        elif isinstance(value, list):
            knob = nuke.Enumeration_Knob(name, nice, value)

        elif isinstance(value, dict):
            if all(isinstance(v, dict) for v in value.values()):
                # Create a group of tabs
                begain = nuke.BeginTabGroup_Knob()
                end = nuke.EndTabGroup_Knob()
                begain.setName(name)
                end.setName(name + "_End")
                knobs.append(begain)
                for k, v in value.items():
                    knobs += create_knobs(v, tab=k)
                knobs.append(end)
            else:
                # Create a group of knobs
                knobs.append(nuke.Tab_Knob(name, nice, nuke.TABBEGINGROUP))
                knobs += create_knobs(value)
                knobs.append(nuke.Tab_Knob(name, nice, nuke.TABENDGROUP))
            continue

        else:
            raise TypeError("Unsupported type: %r" % type(value))

        knobs.append(knob)

    return knobs


def add_publish_knob(node):
    """Add Publish knob to node

    Arguments:
        node (obj): nuke node to be processed

    Returns:
        node (obj): processed nuke node

    """
    if "publish" not in node.knobs():
        body = OrderedDict()
        body[("divd", "")] = Knobby("Text_Knob", "")
        body["publish"] = True
        imprint(node, body)
    return node


def set_avalon_knob_data(node, data=None, prefix="avalon:"):
    """ Sets data into nodes's avalon knob

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
    editable = ["asset", "subset", "name", "namespace"]

    data = data or dict()

    group = OrderedDict()
    body = OrderedDict()

    group["avalonDataGroup"] = body
    body[("warn", "")] = Knobby("Text_Knob",
                                "Warning! Do not change following data!")
    body[("divd", "")] = Knobby("Text_Knob", "")

    for key, value in data.items():
        name = (prefix + key, key)  # Hide prefix on GUI
        if key in editable:
            body[name] = value
        else:
            body[name] = Knobby("Text_Knob", str(value))

    imprint(node, group, tab="AvalonTab")

    return node


def get_avalon_knob_data(node, prefix="avalon:"):
    """ Get data from nodes's avalon knob

    Arguments:
        node (obj): Nuke node to search for data,
        prefix (str, optional): filtering prefix

    Returns:
        data (dict)
    """
    data = {
        knob[len(prefix):]: node[knob].value()
        for knob in node.knobs().keys()
        if knob.startswith(prefix)
    }
    return data


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
