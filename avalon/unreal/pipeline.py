# -*- coding: utf-8 -*-
import sys
import pyblish.api
from ..pipeline import AVALON_CONTAINER_ID

import unreal
from ..tools import (
    projectmanager,
    creator,
    loader,
    publish as publisher,
    sceneinventory,
)

from .. import api
from .lib import (
    move_assets_to_path,
    create_avalon_container,
    create_publish_instance,
)

# from ..lib import logger

self = sys.modules[__name__]
self._menu = "avalonue4"  # Unique name of menu

AVALON_CONTAINERS = "AvalonContainers"


def install():

    pyblish.api.register_host("unreal")
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
    pyblish.api.deregister_host("unreal")


class Creator(api.Creator):
    hosts = ["unreal"]
    asset_types = []

    def process(self):
        nodes = list()

        with unreal.ScopedEditorTransaction("Avalon Creating Instance"):
            if (self.options or {}).get("useSelection"):
                self.log.info("setting ...")
                print("settings ...")
                nodes = unreal.EditorUtilityLibrary.get_selected_assets()

                asset_paths = [a.get_path_name() for a in nodes]
                self.name = move_assets_to_path(
                    "/Game", self.name, asset_paths
                )

            instance = create_publish_instance("/Game", self.name)
            imprint(instance, self.data)

        return instance


class Loader(api.Loader):
    hosts = ["unreal"]


def ls():
    # This needs to have `id registered is project setting for Asset Registry?
    # Is there way to do it with Python? :skull:
    avalon_containers = unreal.EditorAssetLibrary.list_asset_by_tag_value(
        "id", AVALON_CONTAINER_ID
    )

    for asset in avalon_containers:
        data = unreal.EditorAssetLibrary.get_metadata_tag_values(asset)

        yield data


def parse_container(container):
    data = unreal.EditorAssetLibrary.get_metadata_tag_values(container)
    return data


def publish():
    """Shorthand to publish from within host"""
    import pyblish.util

    return pyblish.util.publish()


def containerise(name, namespace, nodes, context, loader=None, suffix="_CON"):

    """Bundles *nodes* (assets) into a *container* and add metadata to it.

    Unreal doesn't support *groups* of assets that you can add metadata to.
    But it does support folders that helps to organize asset. Unfortunately
    those folders are just that - you cannot add any additional information
    to them. `Avalon Integration Plugin`_ is providing way out - Implementing
    `AssetContainer` Blueprint class. This class when added to folder can
    handle metadata on it using standard
    :func:`unreal.EditorAssetLibrary.set_metadata_tag()` and
    :func:`unreal.EditorAssetLibrary.get_metadata_tag_values()`. It also
    stores and monitor all changes in assets in path where it resides. List of
    those assets is available as `assets` property.

    This is list of strings starting with asset type and ending with its path:
    `Material /Game/Avalon/Test/TestMaterial.TestMaterial`

    .. _Avalon Integration Plugin:
        https://github.com/pypeclub/avalon-unreal-integration

    """
    # 1 - create directory for container
    root = "/Game"
    container_name = "{}{}".format(name, suffix)
    new_name = move_assets_to_path(root, container_name, nodes)

    # 2 - create Asset Container there
    path = "{}/{}".format(root, new_name)
    create_avalon_container(container=container_name, path=path)

    data = {
        "schema": "avalon-core:container-2.0",
        "id": AVALON_CONTAINER_ID,
        "name": new_name,
        "namespace": namespace,
        "loader": str(loader),
        "representation": context["representation"]["_id"],
    }

    imprint("{}/{}".format(path, container_name), data)
    return path


def imprint(node, data):
    loaded_asset = unreal.EditorAssetLibrary.load_asset(node)
    for key, value in data.items():
        # Support values evaluated at imprint
        if callable(value):
            value = value()
        # Unreal doesn't support NoneType in metadata values
        if value is None:
            value = ""
        unreal.EditorAssetLibrary.set_metadata_tag(
            loaded_asset, key, str(value)
        )

    with unreal.ScopedEditorTransaction("Avalon containerising"):
        unreal.EditorAssetLibrary.save_asset(node)


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
