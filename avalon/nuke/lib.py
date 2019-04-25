import os
import contextlib
import nuke
import re
import logging
import toml

log = logging.getLogger(__name__)


@contextlib.contextmanager
def maintained_selection():
    nodes = nuke.allNodes()
    previous_selection = [n.name()
                          for n in nodes
                          if n['selected'].value() is True]
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
    nodes = nuke.allNodes()
    [n['selected'].setValue(False) for n in nodes]


def select_nodes(nodes):
    assert isinstance(nodes, (list, tuple)), "nodes has to be list or tuple"
    [n['selected'].setValue(True) for n in nodes]


def add_avalon_tab_knob(node):
    """Adding a tab and a knob into a node
    """
    try:
        avalon_knob = node['avalon'].value()
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


def ls_img_sequence(dirPath, one=None):
    excluding_patterns = ['_broken_', '._', '/.', '.mov', '.jpeg', '.jpg']
    result = {}
    sortedList = []
    files = os.listdir(dirPath)
    for file in files:
        # print file
        for ex in excluding_patterns:
            file_path = os.path.join(dirPath, file).replace('\\', '/')
            if ex in file_path:
                continue
        try:
            prefix, frame, suffix = file.split('.')

            # build a dictionary of the sequences as {name: frames, suffix}
            #
            # eg beauty.01.tif ... beauty.99.tif  will convert to
            # { beauty : [01,02,...,98,99], tif }

            try:
                result[prefix][0].append(frame)
            except KeyError:
                # we have a new file sequence, so create a new key:value pair
                result[prefix] = [[frame], suffix]
        except ValueError:
            # the file isn't in a sequence, add a dummy key:value pair
            if not one:
                result[file] = file
                log.info("!____ result[file]: `{}`".format(result[file]))

    for prefix in result:
        if result[prefix] != prefix:
            frames = result[prefix][0]
            frames.sort()

            # find gaps in sequence
            startFrame = int(frames[0])
            endFrame = int(frames[-1])
            pad = len(frames[0])
            pad_print = '#' * pad
            idealRange = set(range(startFrame, endFrame))
            realFrames = set([int(x) for x in frames])
            # sets can't be sorted, so cast to a list here
            missingFrames = list(idealRange - realFrames)
            missingFrames.sort()

            # calculate fancy ranges
            subRanges = []
            for gap in missingFrames:
                if startFrame != gap:
                    rangeStart = startFrame
                    rangeEnd = gap - 1
                    subRanges.append([rangeStart, rangeEnd])
                startFrame = gap + 1

            subRanges.append([startFrame, endFrame])
            suffix = result[prefix][1]
            sortedList.append({
                'path':
                os.path.join(dirPath, '.'.join([prefix, pad_print,
                                                suffix])).replace('\\', '/'),
                'frames':
                subRanges
            })
        else:
            sortedList.append(prefix)
    if one:
        return sortedList[0]
    else:
        return sortedList


def add_publish_knob(node):
    if "publish" not in node.knobs():
        knob = nuke.Boolean_Knob("publish", "Publish")
        knob.setFlag(0x1000)
        knob.setValue(False)
        node.addKnob(knob)
    return node


def fix_data_for_node_create(data):
    for k, v in data.items():
        try:
            if isinstance(v, unicode):
                data[k] = str(v)
        except Exception:
            data[k] = str(v)

        # if "True" in str(v):
        #     data[k] = True
        # if "False" in str(v):
        #     data[k] = False
        if "0x" in str(v):
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
