import sys

from ..pipeline import AVALON_CONTAINER_ID

import unreal
from ..tools import (
    projectmanager,
    creator,
    loader,
    publish as publisher,
    sceneinventory
)

# from .. import api, schema

# from ..lib import logger

self = sys.modules[__name__]
self._menu = "avalonue4"  # Unique name of menu

AVALON_CONTAINERS = "AvalonContainers"


def install(config):

    # self._menu = api.Session["AVALON_LABEL"] + "menu"
    _register_callbacks()
    _register_events()


def _register_callbacks():
    """
    TODO: Implement callbacks if supported by UE4
    """
    pass


def _register_events():
    """
    TODO: Implement callbacks if supported by UE4
    """
    pass


def uninstall():
    pass


class Creator:
    pass


class Loader:
    pass


def ls():
    avalon_assets = unreal.EditorAssetLibrary.list_asset_by_tag_value(
        'schema', "avalon-core:container-2.0")

    return avalon_assets


def publish():
    """Shorthand to publish from within host"""
    import pyblish.util
    return pyblish.util.publish()


def containerise(asset, context, loader=None):

    data = [
        ("schema", "avalon-core:container-2.0"),
        ("id", AVALON_CONTAINER_ID),
        ("name", asset.rstrip("/").split("/")[-1]),
        ("objectName", asset.rstrip("/").split("/")[-1]),
        ("namespace", asset.rstrip("/").split("/")[:-1]),
        ("loader", str(loader)),
        ("representation", context["representation"]["_id"]),
    ]
    loaded_asset = unreal.EditorAssetLibrary.load_asset(asset)

    for key, value in data:
        if not value:
            continue

        unreal.EditorAssetLibrary.set_metadata_tag(loaded_asset, key, value)

    with unreal.ScopedEditorTransaction("Avalon containerising"):
        unreal.EditorAssetLibrary.save_asset(loaded_asset)


def lock():

    pass


def unlock():
    pass


def is_locked():
    pass


def lock_ignored():
    pass


def show_creator():
    creator.show()


def show_loader():
    loader.show(use_context=True)


def show_publisher():
    publisher.show()


def show_manager():
    sceneinventory.show()


def show_project_manager():
    projectmanager.show()
