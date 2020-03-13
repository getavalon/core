# -*- coding: utf-8 -*-

import contextlib
import unreal


@contextlib.contextmanager
def maintained_selection():
    # WARNING: ❗ this is not implemented at all as I couldn't find way to
    # control selection in Unreal.
    previous_selection = unreal.EditorUtilityLibrary.get_selected_assets()
    try:
        yield
    finally:
        if previous_selection:
            # there is no way to make selection of asset with python?
            pass
        else:
            # And there doesn't seem to be even clear selection command?
            # One in GlobalEditorUtilityBase (select_nothing) doesn't work
            # for me
            pass


def create_folder(root, name):
    """Create new folder

    If folder exists, append number at the end and try again, incrementing
    if needed.

    Args:
        root (str): path root
        name (str): folder name

    Returns:
        str: folder name

    Example:
        >>> create_folder("/Game/Foo")
        /Game/Foo
        >>> create_folder("/Game/Foo")
        /Game/Foo1

    """
    eal = unreal.EditorAssetLibrary
    index = 1
    while True:
        if eal.does_directory_exist("{}/{}".format(root, name)):
            name = "{}{}".format(name, index)
            index += 1
        else:
            eal.make_directory("{}/{}".format(root, name))
            break

    return name


def move_assets_to_path(root, name, assets):
    """
    Moving (renaming) list of asset paths to new destination.

    Args:
        root (str): root of the path (eg. `/Game`)
        name (str): name of destination directory (eg. `Foo` )
        assets (list of str): list of asset paths

    Returns:
        str: folder name

    Example:
        This will get paths of all assets under `/Game/Test` and move them
        to `/Game/NewTest`. If `/Game/NewTest` already exists, then resulting
        path will be `/Game/NewTest1`

        >>> assets = unreal.EditorAssetLibrary.list_assets("/Game/Test")
        >>> move_assets_to_path("/Game", "NewTest", assets)
        NewTest

    """
    eal = unreal.EditorAssetLibrary
    name = create_folder(root, name)

    for asset in assets:
        loaded = eal.load_asset(asset)
        eal.rename_asset(
            asset, "{}/{}/{}".format(root, name, loaded.get_name())
        )

    return name


def create_avalon_container(container, path):
    """
    Helper function to create Avalon Asset Container class on given path.
    This Avalon Asset Class helps to mark given path as Avalon Container
    and enable asset version control on it.

    Args:
        name (str): Asset Container name
        path (str): Path where to create Asset Container. This path should
            point into container folder

    Returns:
        :class:`unreal.Object`: instance of created asset

    Example:

        AvalonHelpers().create_avalon_container(
            "/Game/modelingFooCharacter_CON",
            "modelingFooCharacter_CON"
        )

    """
    factory = unreal.AssetContainerFactory()
    tools = unreal.AssetToolsHelpers().get_asset_tools()

    asset = tools.create_asset(container, path, None, factory)
    return asset


def create_publish_instance(instance, path):
    """
    Helper function to create Avalon Publish Instance  on given path.
    This behaves similary as :func:`create_avalon_container`.

    Args:
        path (str): Path where to create Avalon Publish Instance.
            This path should point into container folder
        name (str): Avalon Publish Instance name

    Returns:
        :class:`unreal.Object`: instance of created asset

    Example:

        AvalonHelpers().create_publish_instance(
            "/Game/modelingFooCharacter_INST",
            "modelingFooCharacter_INST"
        )

    """
    factory = unreal.AssetContainerFactory()
    tools = unreal.AssetToolsHelpers().get_asset_tools()
    asset = tools.create_asset(instance, path, None, factory)
    return asset


class AvalonUnrealException(Exception):
    pass


@unreal.uclass()
class AvalonHelpers(unreal.AvalonLib):
    """
    Class wrapping some useful functions for Avalon.

    This class is extending native BP class in `Avalon Integration Plugin`_

    .. _Avalon Integration Plugin:
        https://github.com/pypeclub/avalon-unreal-integration

    """

    @unreal.ufunction(params=[str, unreal.LinearColor, bool])
    def set_folder_color(self, path, color, force=False):
        """
        This method sets color on folder in Content Browser. Unfortunately
        there is no way to refresh Content Browser so new color isn't applied
        immediately. They are saved to config file and appears correctly
        only after Editor is restarted.

        Args:
            path (str): Path to folder
            color (:class:`unreal.LinearColor`): Color of the folder

        Example:

            AvalonHelpers().set_folder_color(
                "/Game/Path", unreal.LinearColor(a=1.0, r=1.0, g=0.5, b=0)
            )

        Note:
            This will take effect only after Editor is restarted. I couldn't
            find a way to refresh it. Also this saves the color definition
            into the project config, binding this path with color. So if you
            delete this path and later re-create, it will set this color
            again.

        """
        self.c_set_folder_color(path, color, False)
