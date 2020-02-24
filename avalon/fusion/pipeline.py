import sys
import contextlib
import importlib
import logging

import pyblish.api

from .. import api
from ..pipeline import AVALON_CONTAINER_ID
from ..lib import find_submodule


class CompLogHandler(logging.Handler):
    def emit(self, record):
        entry = self.format(record)
        comp = get_current_comp()
        if comp:
            comp.Print(entry)


def ls():
    """List containers from active Fusion scene

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Fusion; once loaded
    they are called 'containers'

    Yields:
        dict: container

    """

    comp = get_current_comp()
    tools = comp.GetToolList(False, "Loader").values()

    has_metadata_collector = False
    config_host = find_submodule(api.registered_config(), "fusion")
    if hasattr(config_host, "collect_container_metadata"):
        has_metadata_collector = True

    for tool in tools:
        container = parse_container(tool)
        if container:

            if has_metadata_collector:
                metadata = config_host.collect_container_metadata(container)
                container.update(metadata)

            yield container


def install():
    """Install Fusion-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(fusion)`.

    """

    # TODO: Register Fusion callbacks
    # TODO: Set project
    # TODO: Install Fusion menu (this is done with config .fu script actually)

    pyblish.api.register_host("fusion")

    # Remove all handlers associated with the root logger object, because
    # that one sometimes logs as "warnings" incorrectly.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Attach default logging handler that prints to active comp
    logger = logging.getLogger()
    formatter = logging.Formatter(fmt="%(message)s\n")
    handler = CompLogHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def uninstall():
    """Uninstall Fusion-specific functionality of avalon-core.

    This function is called automatically on calling `api.uninstall()`.
    """

    pyblish.api.deregister_host("fusion")


def imprint_container(tool,
                      name,
                      namespace,
                      context,
                      loader=None):
    """Imprint a Loader with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        tool (object): The node in Fusion to imprint as container, usually a
            Loader.
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        context (dict): Asset information
        loader (str, optional): Name of loader used to produce this container.

    Returns:
        None

    """

    data = [
        ("schema", "avalon-core:container-2.0"),
        ("id", AVALON_CONTAINER_ID),
        ("name", str(name)),
        ("namespace", str(namespace)),
        ("loader", str(loader)),
        ("representation", str(context["representation"]["_id"])),
    ]

    for key, value in data:
        tool.SetData("avalon.{}".format(key), value)


def parse_container(tool):
    """Returns imprinted container data of a tool

    This reads the imprinted data from `imprint_container`.

    """

    data = tool.GetData('avalon')
    if not isinstance(data, dict):
        return

    # If not all required data return the empty container
    required = ['schema', 'id', 'name',
                'namespace', 'loader', 'representation']
    if not all(key in data for key in required):
        return

    container = {key: data[key] for key in required}

    # Store the tool's name
    container["objectName"] = tool.Name

    # Store reference to the tool object
    container["_tool"] = tool

    return container


def get_current_comp():
    """Hack to get current comp in this session"""
    fusion = getattr(sys.modules["__main__"], "fusion", None)
    return fusion.CurrentComp if fusion else None


@contextlib.contextmanager
def comp_lock_and_undo_chunk(comp, undo_queue_name="Script CMD"):
    """Lock comp and open an undo chunk during the context"""
    try:
        comp.Lock()
        comp.StartUndo(undo_queue_name)
        yield
    finally:
        comp.Unlock()
        comp.EndUndo()
