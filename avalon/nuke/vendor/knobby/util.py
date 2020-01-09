import sys
import re
import nuke

from . import parser


if sys.version_info[0] == 3:  # PY3
    string_types = str
else:
    import __builtin__

    string_types = __builtin__.basestring


def imprint(node, data, tab=None):
    """Store attributes with value on node

    Parse user data into Node knobs.
    Use `collections.OrderedDict` to ensure knob order.

    Args:
        node(nuke.Node): node object from Nuke
        data(dict): collection of attributes and their value
        tab (str, optional): Tab name, default "User"

    Returns:
        None

    """
    tab = tab or "User"

    existed_knobs = node.knobs()
    tab_existed = tab in existed_knobs

    def add_knobs(knobs, tab):
        node.addKnob(nuke.Tab_Knob(tab))
        for knob in knobs:
            node.addKnob(knob)

    if tab_existed:
        TEMP = ":::temp_imprint_tab:::"
        new_tab = TEMP + tab

        new_knobs = list()
        for knob in create_knobs(data, tab=new_tab):
            name = knob.name()[len(TEMP):]
            if name in existed_knobs and knob.Class() != "Tab_Knob":
                existed_knobs[name].setValue(knob.value())
            else:
                new_knobs.append(knob)

        old_tcl = node.writeKnobs(nuke.TO_SCRIPT | nuke.WRITE_USER_KNOB_DEFS)
        old_tcl = old_tcl.strip()

        add_knobs(new_knobs, new_tab)

        new_tcl = node.writeKnobs(nuke.TO_SCRIPT | nuke.WRITE_USER_KNOB_DEFS)
        new_tcl = new_tcl.strip()[len(old_tcl) + 1:].replace(TEMP, "")

        first_user_knob = _parse_first_user_knob(node)
        for knob in reversed(node.allKnobs()):
            knob_name = knob.name()
            node.removeKnob(knob)
            if knob_name == first_user_knob:
                break

        tablet = parser.parse(old_tcl)
        tablet.merge(parser.parse(new_tcl))
        node.readKnobs(tablet.to_script())

    else:
        new_knobs = create_knobs(data, tab=tab)
        add_knobs(new_knobs, tab)


class Knobby(object):
    """For creating knob which it's type isn't mapped in `create_knobs`

    Args:
        type (string): Nuke knob type name
        value: Value to be set with `Knob.setValue`, put `None` if not required
        flags (list, optional): Knob flags to be set with `Knob.setFlag`
        *args: Args other than knob name for initializing knob class

    """

    def __init__(self, type, value, flags=None, *args):
        self.type = type
        self.value = value
        self.flags = flags or []
        self.args = args

    def create(self, name, nice=None):
        knob_cls = getattr(nuke, self.type)
        knob = knob_cls(name, nice, *self.args)
        if self.value is not None:
            knob.setValue(self.value)
        for flag in self.flags:
            knob.setFlag(flag)
        return knob


def create_knobs(data, tab):
    """Create knobs by data

    Depending on the type of each dict value and creates the correct Knob.

    Mapped types:
        bool: nuke.Boolean_Knob
        int: nuke.Int_Knob
        float: nuke.Double_Knob
        list: nuke.Enumeration_Knob
        string_types: nuke.String_Knob

        dict: If it's a nested dict (all values are dict), will turn into
            A tabs group. Or just a knobs group.

    Args:
        data (dict): collection of attributes and their value
        prefix (str): knob name prefix

    Returns:
        list: A list of `nuke.Knob` objects

    """
    def nice_naming(key):
        """Convert camelCase name into UI Display Name"""
        words = re.findall('[A-Z][^A-Z]*', key[0].upper() + key[1:])
        return " ".join(words)

    # Turn key-value pairs into knobs
    knobs = list()
    prefix = tab + ":"

    for key, value in data.items():
        # Knob name
        if isinstance(key, tuple):
            name, nice = key
        else:
            name, nice = key, nice_naming(key)

        name = prefix + name

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

        elif isinstance(value, string_types):
            knob = nuke.String_Knob(name, nice)
            knob.setValue(value)

        elif isinstance(value, list):
            knob = nuke.Enumeration_Knob(name, nice, value)

        elif isinstance(value, dict):
            if all(isinstance(v, dict) for v in value.values()):
                # Create a group of tabs
                begin = nuke.BeginTabGroup_Knob(name)
                end = nuke.EndTabGroup_Knob()
                begin.setName(name)
                begin.setLabel(nice)
                end.setName(name)
                knobs.append(begin)
                for k, v in value.items():
                    tab_name = "%s:%s" % (name, k)
                    knobs.append(nuke.Tab_Knob(tab_name, k))
                    knobs += create_knobs(v, tab=tab_name)
                knobs.append(end)
            else:
                # Create a group of knobs
                knobs.append(nuke.Tab_Knob(name, nice, nuke.TABBEGINGROUP))
                knobs += create_knobs(value, tab=name)
                knobs.append(nuke.Tab_Knob(name, nice, nuke.TABENDGROUP))
            continue

        else:
            raise TypeError("Unsupported type: %r" % type(value))

        knobs.append(knob)

    return knobs


EXCLUDED_KNOB_TYPE_ON_READ = (
    20,  # Tab Knob
    26,  # Text Knob (But for backward compatibility, still be read
         #            if value is not an empty string.)
)

KNOB_PATTERN = re.compile(
    "(?<=addUserKnob {)"
    "([0-9]*) (\\S*)"  # Matching knob type and knob name
    "(?=[ |}])"
)


def _parse_first_user_knob(node):
    tcl = node.writeKnobs(nuke.WRITE_USER_KNOB_DEFS)
    matched = KNOB_PATTERN.search(tcl)
    if matched:
        return matched.group(2)


def read(node, filter=None):
    """Return user-defined knobs from given `node`

    Args:
        node (nuke.Node): Nuke node object
        filter (func, optional): Function for filtering knobs by
            knob name prefix and remove prefix as data entry name.
            If not provided, all user-defined knobs will be read.

    Returns:
        dict

    """
    data = dict()
    filter = filter or (lambda name: name)

    first_user_knob = _parse_first_user_knob(node)
    if first_user_knob is not None:
        # Collect user knobs from the end of the knob list
        for knob in reversed(node.allKnobs()):
            knob_name = knob.name()
            if not knob_name:
                # Ignore unnamed knob
                continue

            knob_type = nuke.knob(knob.fullyQualifiedName(), type=True)
            value = knob.value()

            if (
                knob_type not in EXCLUDED_KNOB_TYPE_ON_READ or
                # For compating read-only string data that imprinted
                # by `nuke.Text_Knob`.
                (knob_type == 26 and value)
            ):
                key = filter(knob_name)
                if key:
                    data[key] = value

            if knob_name == first_user_knob:
                break

    return data


def mold(node, tab=None, map_cls=None):
    """Return user-defined knobs from given `node` with hierarchy

    Args:
        node (nuke.Node): Nuke node object
        tab (str, optional): Target tab name. If given, only read
            knobs of this tab.
        map_cls (Mapping type class, optional): Default `dict`, use
            `collections.OrderedDict` if orders need to be preserved.

    Returns:
        Instance of `map_cls`

    """
    knobs = node.knobs()
    target = (tab or "") + ":"

    map_cls = map_cls or dict

    def _mold(tablet, prefix=None):
        data = map_cls()
        prefix = (prefix + ":") if prefix else ""

        name = tablet.name or ""
        abs_name = name + ":"
        all_elem = abs_name.startswith(target) if tab and name else True

        for item in tablet:
            if isinstance(item, parser.Tablet):
                name = item.name
                abs_name = name + ":"

                if tab and target.startswith(abs_name):

                    data = _mold(item, prefix=name)

                elif all_elem:

                    key = name[len(prefix):] if prefix else name
                    data[key] = _mold(item, prefix=name)

            elif all_elem:

                matched = KNOB_PATTERN.search(item)
                if not matched:
                    raise TypeError("Knob name can not be identified.")
                else:
                    name = matched.group(2)
                    knob = knobs[name]
                    key = name[len(prefix):] if prefix else name
                    data[key] = knob.value()

        return data

    tcl = node.writeKnobs(nuke.WRITE_USER_KNOB_DEFS)
    tablet = parser.parse(tcl)

    return _mold(tablet)
