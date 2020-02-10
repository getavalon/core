import json
import contextlib

from . import com_objects
from ..tools import html_server


def Dispatch(application):
    """Wrapped Dispatch function.

    This could later query whether the platform is Windows or Mac.

    Args:
        application (str): Application to dispatch.
    """
    from win32com.client import Dispatch
    return Dispatch(application)


def app():
    """Convenience function to get the Photoshop app.

    This could later query whether the platform is Windows or Mac.

    This needs to be a function call because when calling Dispatch directly
    from a different thread will result in "CoInitialize has not been called"
    which can be fixed with pythoncom.CoInitialize(). However even then it will
    still error with "The application called an interface that was marshalled
    for a different thread"
    """
    return Dispatch("Photoshop.Application")


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
    _app = app()

    layers_data = {}
    try:
        layers_data = json.loads(_app.ActiveDocument.Info.Headline)
    except json.decoder.JSONDecodeError:
        pass

    # json.dumps writes integer values in a dictionary to string, so
    # anticipating it here.
    if str(layer.id) in layers_data:
        layers_data[str(layer.id)].update(data)
    else:
        layers_data[str(layer.id)] = data

    # Ensure only valid ids are stored.
    layer_ids = []
    for layer in get_layers_in_document():
        layer_ids.append(layer.id)

    cleaned_data = {}
    for id in layers_data:
        if int(id) in layer_ids:
            cleaned_data[id] = layers_data[id]

    # Write date to FileInfo headline.
    _app.ActiveDocument.Info.Headline = json.dumps(cleaned_data, indent=4)


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

    _app = app()

    ref = Dispatch("Photoshop.ActionReference")
    ref.PutClass(_app.StringIDToTypeID("layerSection"))

    lref = Dispatch("Photoshop.ActionReference")
    lref.PutEnumerated(
        _app.CharIDToTypeID("Lyr "),
        _app.CharIDToTypeID("Ordn"),
        _app.CharIDToTypeID("Trgt")
    )

    desc = Dispatch("Photoshop.ActionDescriptor")
    desc.PutReference(_app.CharIDToTypeID("null"), ref)
    desc.PutReference(_app.CharIDToTypeID("From"), lref)

    _app.ExecuteAction(
        _app.CharIDToTypeID("Mk  "),
        desc,
        com_objects.constants().psDisplayNoDialogs
    )


def get_selected_layers():
    """Get the selected layers

    Returns:
        list
    """
    _app = app()

    group_selected_layers()

    selection = list(_app.ActiveDocument.ActiveLayer.Layers)

    _app.ExecuteAction(
        _app.CharIDToTypeID("undo"),
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
    _app = app()

    ref = Dispatch("Photoshop.ActionReference")
    for id in [x.id for x in layers]:
        ref.PutIdentifier(_app.CharIDToTypeID("Lyr "), id)

    desc = Dispatch("Photoshop.ActionDescriptor")
    desc.PutReference(_app.CharIDToTypeID("null"), ref)
    desc.PutBoolean(_app.CharIDToTypeID("MkVs"), False)

    _app.ExecuteAction(
        _app.CharIDToTypeID("slct"),
        desc,
        com_objects.constants().psDisplayNoDialogs
    )


def _recurse_layers(layers):
    """Recursively get layers in provided layers.

    Args:
        layers (list): List of COMObjects.

    Returns:
        List of COMObjects.
    """
    result = {}
    for layer in layers:
        result[layer.id] = layer
        if layer.LayerType == com_objects.constants().psLayerSet:
            result.update(_recurse_layers(list(layer.Layers)))

    return result


def get_layers_in_layers(layers):
    """Get all layers in layers."""
    return list(_recurse_layers(layers).values())


def get_layers_in_document(document=None):
    """Get all layers in a document.

    Args:
        document (win32com.client.CDispatch): COMObject of the document. If
            None is supplied the ActiveDocument is used.
    """
    document = document or app().ActiveDocument
    return list(_recurse_layers(list(x for x in document.Layers)).values())


def import_smart_object(path):
    """Import the file at `path` as a smart object to active document.

    Args:
        path (str): File path to import.
    """
    _app = app()

    desc1 = Dispatch("Photoshop.ActionDescriptor")
    desc1.PutPath(_app.CharIDToTypeID("null"), path)
    desc1.PutEnumerated(
        _app.CharIDToTypeID("FTcs"),
        _app.CharIDToTypeID("QCSt"),
        _app.CharIDToTypeID("Qcsa")
    )

    desc2 = Dispatch("Photoshop.ActionDescriptor")
    desc2.PutUnitDouble(
        _app.CharIDToTypeID("Hrzn"), _app.CharIDToTypeID("#Pxl"), 0.0
    )
    desc2.PutUnitDouble(
        _app.CharIDToTypeID("Vrtc"), _app.CharIDToTypeID("#Pxl"), 0.0
    )

    desc1.PutObject(
        _app.CharIDToTypeID("Ofst"), _app.CharIDToTypeID("Ofst"), desc2
    )

    _app.ExecuteAction(
        _app.CharIDToTypeID("Plc "),
        desc1,
        com_objects.constants().psDisplayNoDialogs
    )
    layer = get_selected_layers()[0]
    layer.MoveToBeginning(_app.ActiveDocument)

    return layer


def replace_smart_object(layer, path):
    """Replace the smart object `layer` with file at `path`

    Args:
        layer (win32com.client.CDispatch): COMObject of the layer.
        path (str): File to import.
    """
    _app = app()

    _app.ActiveDocument.ActiveLayer = layer

    desc = Dispatch("Photoshop.ActionDescriptor")
    desc.PutPath(_app.CharIDToTypeID("null"), path.replace("\\", "/"))
    desc.PutInteger(_app.CharIDToTypeID("PgNm"), 1)

    _app.ExecuteAction(
        _app.StringIDToTypeID("placedLayerReplaceContents"),
        desc,
        com_objects.constants().psDisplayNoDialogs
    )
