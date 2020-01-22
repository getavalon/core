import os
import sys
import platform
import json
from distutils.dir_util import copy_tree


def get_engine_versions():
    """
    This will try to detect location and versions of installed Unreal Engine.
    Location can be overridden by `UNREAL_ENGINE_LOCATION` environment
    variable.

    Returns dictionary with version as a key and dir as value.
    """
    try:
        engine_locations = {}
        root, dirs, files = next(os.walk(os.environ["UNREAL_ENGINE_LOCATION"]))

        for dir in dirs:
            if dir.startswith('UE_'):
                ver = dir.split('_')[1]
                engine_locations[ver] = os.path.join(root, dir)
    except KeyError:
        # environment variable not set
        pass
    except OSError:
        # specified directory doesn't exists
        pass

    # if we've got something, break autodetection process
    if engine_locations:
        return engine_locations

    # else kick in platform specific detection
    if platform.system().lower() == 'windows':
        return _win_get_engine_versions()
    elif platform.system().lower() == 'linux':
        # on linux, there is no installation and getting Unreal Engine involves
        # git clone. So we'll probably depend on `UNREAL_ENGINE_LOCATION`.
        pass
    elif platform.system().lower() == 'darwin':
        return _darwin_get_engine_version()

    return {}


def _win_get_engine_versions():
    """
    If engines are installed via Epic Games Launcher then there is:
    `%PROGRAMDATA%/Epic/UnrealEngineLauncher/LauncherInstalled.dat`
    This file is JSON file listing installed stuff, Unreal engines
    are marked with `"AppName" = "UE_X.XX"`` like `UE_4.24`
    """
    install_json_path = os.path.join(
        os.environ.get('PROGRAMDATA'),
        'Epic', 'UnrealEngineLauncher', 'LauncherInstalled.dat')

    return _parse_launcher_locations(install_json_path)


def _darwin_get_engine_version():
    """
    It works the same as on Windows, just JSON file location is different.
    """
    install_json_path = os.path.join(
        os.environ.get('HOME'),
        'Library', 'Application Support', 'Epic',
        'UnrealEngineLauncher', 'LauncherInstalled.dat')

    return _parse_launcher_locations(install_json_path)


def _parse_launcher_locations(install_json_path):
    engine_locations = {}
    if os.path.isfile(install_json_path):
        with open(install_json_path, 'r') as ilf:
            try:
                install_data = json.load(ilf)
            except json.JSONDecodeError:
                raise Exception('Invalid `LauncherInstalled.dat file. `'
                                'Cannot determine Unreal Engine location.')

        for installation in install_data.get('installationList', []):
            if installation.get('AppName').startswith('UE_'):
                ver = installation.get('AppName').split('_')[1]
                engine_locations[ver] = installation.get('InstallLocation')

    return engine_locations


def create_unreal_project(project_name, ue_version, dir):
    """
    This will create `.uproject` file at specified location. As there is no
    way I know to create project via command line, this is easiest option.
    Unreal project file is basically JSON file. If we find
    `AVALON_UNREAL_PLUGIN` environment variable we assume this is location
    of Avalon Integration Plugin and we copy its content to project folder
    and enable this plugin.
    """

    module = []
    if os.path.isdir(os.environ.get('AVALON_UNREAL_PLUGIN', '')):
        module = [
            {
                "Name": "Avalon",
                "Type": "Runtime",
                "LoadingPhase": "Default",
                "AdditionalDependencies": [
                    "Engine"
                ]
            }
        ]
        # copy plugin to correct path under project
        plugin_path = os.path.join(dir, 'Plugins', 'Avalon')
        os.makedirs(plugin_path, exist_ok=True)
        copy_tree(os.environ.get('AVALON_UNREAL_PLUGIN'), plugin_path)

    data = {
        'FileVersion': 3,
        'EngineAssociation': ue_version,
        'Category': '',
        'Description': '',
        'Modules': module,
        "Plugins": [
            {
                "Name": "PythonScriptPlugin",
                "Enable": True
            }
        ]
    }

    project_file = os.path.join(dir, "{}.uproject".format(project_name))
    with open(project_file, mode='w') as pf:
        json.dump(data, pf)
