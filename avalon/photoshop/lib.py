import json
import contextlib
import functools

from win32com.client import Dispatch

from . import com_objects
from ..tools import html_server

# Convinience variable that could later query whether the platform is Windows
# or Mac.
# This needs to be a partial function we can later call because when calling
# Dispatch directly from a different thread will result first a
# "CoInitialize has not been called.", which can be fixed with
# pythoncom.CoInitialize() but secondly "The application called an interface
# that was marshalled for a different thread".
app = functools.partial(Dispatch, "Photoshop.Application")


def start_server():
    """Starts the web server that will be hosted in the Photoshop extension"""
    from avalon import api, photoshop

    api.install(photoshop)
    html_server.app.start_server(5000)


def imprint(layer, data):
    """Write `data` to the active document "headline" field as json.

    Arguments:
        layer (win32com.client.CDispatch): COMObject of the layer.
        data (dict): Dictionary of key/value pairs.

    Example:
        >>> from avalon.photoshop import lib
        >>> layer = app.ActiveDocument.ArtLayers.Add()
        >>> data = {"str": "someting", "int": 1, "float": 0.32, "bool": True}
        >>> lib.imprint(layer, data)
    """
    layers_data = {}
    try:
        layers_data = json.loads(app().ActiveDocument.Info.Headline)
    except json.decoder.JSONDecodeError:
        pass

    # json.dumps writes integer values in a dictionary to string, so
    # anticipating it here.
    if str(layer.id) in layers_data:
        layers_data[str(layer.id)].update(data)
    else:
        layers_data[str(layer.id)] = data

    app().ActiveDocument.Info.Headline = json.dumps(layers_data, indent=4)


def read(layer):
    """Read the layer metadata in to a dict

    Args:
        layer (win32com.client.CDispatch): COMObject of the layer.

    Returns:
        dict
    """
    layers_data = {}
    try:
        layers_data = json.loads(app().ActiveDocument.Info.Headline)
    except json.decoder.JSONDecodeError:
        pass

    return layers_data.get(str(layer.id))


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context."""
    selection = get_selected_layers()
    try:
        yield selection
    finally:
        select_layers(selection)


@contextlib.contextmanager
def maintained_visibility():
    """Maintain visibility during context."""
    visibility = {}
    layers = get_layers_in_document(app().ActiveDocument)
    for layer in layers:
        visibility[layer.id] = layer.Visible
    try:
        yield
    finally:
        for layer in layers:
            layer.Visible = visibility[layer.id]


def group_selected_layers():
    """Create a group and adds the selected layers."""

    ref = Dispatch("Photoshop.ActionReference")
    ref.PutClass(app().StringIDToTypeID("layerSection"))

    lref = Dispatch("Photoshop.ActionReference")
    lref.PutEnumerated(
        app().CharIDToTypeID("Lyr "),
        app().CharIDToTypeID("Ordn"),
        app().CharIDToTypeID("Trgt")
    )

    desc = Dispatch("Photoshop.ActionDescriptor")
    desc.PutReference(app().CharIDToTypeID("null"), ref)
    desc.PutReference(app().CharIDToTypeID("From"), lref)

    app().ExecuteAction(
        app().CharIDToTypeID("Mk  "),
        desc,
        com_objects.constants().psDisplayNoDialogs
    )


def get_selected_layers():
    """Get the selected layers

    Returns:
        list
    """
    group_selected_layers()

    selection = [x for x in app().ActiveDocument.ActiveLayer.Layers]

    app().ExecuteAction(
        app().CharIDToTypeID("undo"),
        None,
        com_objects.constants().psDisplayNoDialogs
    )

    return selection


def get_layers_by_ids(ids):
    return [x for x in app().ActiveDocument.Layers if x.id in ids]


def select_layers(layers):
    """Selects multiple layers

    Args:
        layers (list): List of COMObjects.
    """
    ref = Dispatch("Photoshop.ActionReference")
    for id in [x.id for x in layers]:
        ref.PutIdentifier(app().CharIDToTypeID("Lyr "), id)

    desc = Dispatch("Photoshop.ActionDescriptor")
    desc.PutReference(app().CharIDToTypeID("null"), ref)
    desc.PutBoolean(app().CharIDToTypeID("MkVs"), False)

    app().ExecuteAction(
        app().CharIDToTypeID("slct"),
        desc,
        com_objects.constants().psDisplayNoDialogs
    )


def _recurse_layers(layers):
    result = {}
    for layer in layers:
        result[layer.id] = layer
        if layer.LayerType == com_objects.constants().psLayerSet:
            result.update(_recurse_layers([*layer.Layers]))

    return result


def get_layers_in_layers(layers):
    """Get all layers in layers."""
    return list(_recurse_layers(layers).values())


def get_layers_in_document(document=None):
    """Get all layers recursively in a document."""
    document = document or app().ActiveDocument
    return list(_recurse_layers([*document.Layers]).values())


def import_smart_object(path):
    desc1 = Dispatch("Photoshop.ActionDescriptor")
    desc1.PutPath(app().CharIDToTypeID("null"), path)
    desc1.PutEnumerated(
        app().CharIDToTypeID("FTcs"),
        app().CharIDToTypeID("QCSt"),
        app().CharIDToTypeID("Qcsa")
    )

    desc2 = Dispatch("Photoshop.ActionDescriptor")
    desc2.PutUnitDouble(
        app().CharIDToTypeID("Hrzn"), app().CharIDToTypeID("#Pxl"), 0.0
    )
    desc2.PutUnitDouble(
        app().CharIDToTypeID("Vrtc"), app().CharIDToTypeID("#Pxl"), 0.0
    )

    desc1.PutObject(
        app().CharIDToTypeID("Ofst"), app().CharIDToTypeID("Ofst"), desc2
    )

    app().ExecuteAction(
        app().CharIDToTypeID("Plc "),
        desc1,
        com_objects.constants().psDisplayNoDialogs
    )
    layer = get_selected_layers()[0]
    layer.MoveToBeginning(app().ActiveDocument)

    return layer


def replace_smart_object(layer, path):
    app().ActiveDocument.ActiveLayer = layer

    desc = Dispatch("Photoshop.ActionDescriptor")
    desc.PutPath(app().CharIDToTypeID("null"), path.replace("\\", "/"))
    desc.PutInteger(app().CharIDToTypeID("PgNm"), 1)

    app().ExecuteAction(
        app().StringIDToTypeID("placedLayerReplaceContents"),
        desc,
        com_objects.constants().psDisplayNoDialogs
    )
