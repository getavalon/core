import re
import os
import sys
import contextlib

from .pipeline import get_current_script


@contextlib.contextmanager
def maintained_selection():
    nuke = getattr(sys.modules["__main__"], "nuke", None)
    root, nodes = get_current_script(nuke)
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


def get_frame_path(path):
    """Get filename for the Fusion Saver with padded number as '#'

    >>> get_frame_path("C:/test.exr")
    ('C:/test', 4, '.exr')

    >>> get_frame_path("filename.00.tif")
    ('filename.', 2, '.tif')

    >>> get_frame_path("foobar35.tif")
    ('foobar', 2, '.tif')

    Args:
        path (str): The path to render to.

    Returns:
        tuple: head, padding, tail (extension)

    """
    filename, ext = os.path.splitext(path)

    # Find a final number group
    match = re.match('.*?([0-9]+)$', filename)
    if match:
        padding = len(match.group(1))
        # remove number from end since fusion
        # will swap it with the frame number
        filename = filename[:-padding]
    else:
        padding = 4  # default Fusion padding

    return filename, padding, ext


def add_publish_knob(node):
    if "publish" not in node.knobs():
        knob = nuke.Boolean_Knob("publish", "Publish")
        knob.setValue(False)
        node.addKnob(knob)
    return node
