import subprocess
import threading
import os
import random
import zipfile
import sys
import importlib
import queue
import shutil
import logging
import contextlib
import json

from .server import Server
from ..vendor.Qt import QtWidgets

self = sys.modules[__name__]
self.server = None
self.pid = None
self.application_path = None
self.callback_queue = None
self.workfile_path = None

# Setup logging.
self.log = logging.getLogger(__name__)
self.log.setLevel(logging.DEBUG)


def execute_in_main_thread(func_to_call_from_main_thread):
    self.callback_queue.put(func_to_call_from_main_thread)


def main_thread_listen():
    callback = self.callback_queue.get()
    callback()


def launch(application_path, scene_path=None):
    """Setup for Harmony launch.

    Launches Harmony and the server, then starts listening on the main thread
    for callbacks from the server. This is to have Qt applications run in the
    main thread.
    """
    from avalon import api, harmony

    api.install(harmony)

    port = random.randrange(5000, 6000)
    os.environ["AVALON_HARMONY_PORT"] = str(port)
    self.application_path = application_path

    # Launch Harmony.
    os.environ["TOONBOOM_GLOBAL_SCRIPT_LOCATION"] = os.path.dirname(__file__)

    path = scene_path
    if not scene_path:
        harmony_path = os.path.join(
            os.path.expanduser("~"), ".avalon", "harmony"
        )
        zip_file = os.path.join(os.path.dirname(__file__), "temp_scene.zip")
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(harmony_path)

        path = os.path.join(harmony_path, "temp", "temp.xstage")

    process = subprocess.Popen([application_path, path])

    self.pid = process.pid

    # Launch Avalon server.
    self.server = Server(port)
    thread = threading.Thread(target=self.server.start)
    thread.deamon = True
    thread.start()

    if not scene_path:
        self.callback_queue = queue.Queue()
        while True:
            main_thread_listen()


def on_file_changed(path):
    """Threaded zipping and move of the project directory.

    This method is called when the `.xstage` file is changed.
    """

    self.log.debug("File changed: " + path)

    if self.workfile_path is None:
        return

    thread = threading.Thread(
        target=zip_and_move, args=(os.path.dirname(path), self.workfile_path)
    )
    thread.start()


def zip_and_move(source, destination):
    """Zip a directory and move to `destination`

    Args:
        - source (str): Directory to zip and move to destination.
        - destination (str): Destination file path to zip file.
    """
    os.chdir(os.path.dirname(source))
    shutil.make_archive(os.path.basename(source), "zip", source)
    shutil.move(os.path.basename(source) + ".zip", destination)
    self.log.debug("Saved \"{}\" to \"{}\"".format(source, destination))


def show(module_name):
    """Call show on "module_name".

    This allows to make a QApplication ahead of time and always "exec_" to
    prevent crashing.

    Args:
        module_name (str): Name of module to call "show" on.
    """
    # Need to have an existing QApplication.
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    # Import and show tool.
    module = importlib.import_module(module_name)
    module.show()

    # QApplication needs to always execute.
    if "publish" in module_name:
        return

    app.exec_()


def read(node):
    """Read the node metadata in to a dictionary.

    Args:
        node (str): Path to node.

    Returns:
        dict
    """

    func = """function read(node_path)
    {
        return node.getTextAttr(node_path, 1.0, "avalon");
    }
    read
    """
    try:
        return json.loads(
            self.send({"function": func, "args": [node]})["result"]
        )
    except json.decoder.JSONDecodeError:
        return {}


def imprint(node, data):
    """Write `data` to the `node` as json.

    Arguments:
        node (str): Path to node.
        data (dict): Dictionary of key/value pairs.

    Example:
        >>> from avalon.harmony import lib
        >>> node = "Top/Display"
        >>> data = {"str": "someting", "int": 1, "float": 0.32, "bool": True}
        >>> lib.imprint(layer, data)
    """

    node_data = read(node)
    node_data.update(data)

    func = """function imprint(args)
    {
        var node_path = args[0];
        var data = args[1];
        node.createDynamicAttr(
            node_path, "STRING", "avalon", "Avalon Metadata", false
        );
        node.setTextAttr(
            node_path,
            "avalon",
            1.0,
            JSON.stringify(data)
        );
    }
    imprint
    """
    self.send({"function": func, "args": [node, node_data]})


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context."""

    func = """function get_selection_nodes()
    {
        var selection_length = selection.numberOfNodesSelected();
        var selected_nodes = [];
        for (var i = 0 ; i < selection_length; i++)
        {
            selected_nodes.push(selection.selectedNode(i));
        }
        return selected_nodes
    }
    get_selection_nodes
    """
    selected_nodes = self.send({"function": func})["result"]

    func = """function select_nodes(node_paths)
    {
        selection.clearSelection();
        for (var i = 0 ; i < node_paths.length; i++)
        {
            selection.addNodeToSelection(node_paths[i]);
        }
    }
    select_nodes
    """
    try:
        yield selected_nodes
    finally:
        selected_nodes = self.send(
            {"function": func, "args": selected_nodes}
        )


def send(request):
    """Public method for sending requests to Harmony."""
    return self.server.send(request)


@contextlib.contextmanager
def maintained_nodes_state(nodes):
    """Maintain nodes states during context."""
    # Collect current state.
    states = []
    for node in nodes:
        states.append(
            self.send(
                {"function": "node.getEnable", "args": [node]}
            )["result"]
        )

    # Disable all nodes.
    func = """function func(nodes)
    {
        for (var i = 0 ; i < nodes.length; i++)
        {
            node.setEnable(nodes[i], false);
        }
    }
    func
    """
    self.send({"function": func, "args": [nodes]})

    # Restore state after yield.
    func = """function func(args)
    {
        var nodes = args[0];
        var states = args[1];
        for (var i = 0 ; i < nodes.length; i++)
        {
            node.setEnable(nodes[i], states[i]);
        }
    }
    func
    """

    try:
        yield
    finally:
        self.send({"function": func, "args": [nodes, states]})
