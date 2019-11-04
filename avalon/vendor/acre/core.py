import logging
import json
import re
import os
import platform

from . import lib


PLATFORM = platform.system().lower()

logging.basicConfig()
log = logging.getLogger()


class CycleError(ValueError):
    """A cyclic dependency in dynamic environment"""
    pass


class DynamicKeyClashError(ValueError):
    """A dynamic key clash on compute"""
    pass


def compute(env,
            dynamic_keys=True,
            allow_cycle=False,
            allow_key_clash=False,
            cleanup=True):
    """Compute the result from recursive dynamic environment.

    Note: Keys that are not present in the data will remain unformatted as the
        original keys. So they can be formatted against the current user
        environment when merging. So {"A": "{key}"} will remain {key} if not
        present in the dynamic environment.

    """
    # TODO: A reference to itself should be "maintained" and not cause cycle
    #       Thus format dynamic values and keys, except those referencing
    #       itself since they are intended to append to current user env
    env = env.copy()

    # Collect dependencies
    dependencies = []
    for key, value in env.items():
        dependent_keys = re.findall("{(.+?)}", value)
        for dependency in dependent_keys:
            # Ignore direct references to itself because
            # we don't format with itself anyway
            if dependency == key:
                continue

            dependencies.append((key, dependency))

    result = lib.topological_sort(dependencies)

    # Check cycle
    if result.cyclic:
        if not allow_cycle:
            raise CycleError("A cycle is detected on: "
                             "{0}".format(result.cyclic))
        log.warning("Cycle detected. Result might "
                    "be unexpected for: %s", result.cyclic)

    # Format dynamic values
    for key in reversed(result.sorted):
        if key in env:
            data = env.copy()
            data.pop(key)    # format without itself
            env[key] = lib.partial_format(env[key], data=data)

    # Format cyclic values
    for key in result.cyclic:
        if key in env:
            data = env.copy()
            data.pop(key)   # format without itself
            env[key] = lib.partial_format(env[key], data=data)

    # Format dynamic keys
    if dynamic_keys:
        formatted = {}
        for key, value in env.items():
            new_key = lib.partial_format(key, data=env)

            if new_key in formatted:
                if not allow_key_clash:
                    raise DynamicKeyClashError("Key clashes on: {0} "
                                               "(source: {1})".format(new_key,
                                                                      key))
                log.warning("Key already in formatted dict: %s", new_key)

            formatted[new_key] = value
        env = formatted

    if cleanup:
        separator = os.pathsep
        for key, value in env.items():
            paths = value.split(separator)

            # Keep unique path entries: {A};{A};{B} -> {A};{B}
            paths = lib.uniqify_ordered(paths)

            # Remove empty values
            paths = [p for p in paths if p.strip()]

            value = separator.join(paths)
            env[key] = value

    return env


def parse(env, platform_name=None):
    """Parse environment for platform-specific values

    Args:
        env (dict): The source environment to read.
        platform_name (str, Optional): Name of platform to parse for.
            This can be "windows", "darwin" or "linux".
            Defaults to the currently active platform.

    Returns:
        dict: The flattened environment for a platform.

    """

    platform_name = platform_name or PLATFORM

    result = {}
    for variable, value in env.items():

        # Platform specific values
        if isinstance(value, dict):
            value = value.get(platform_name, "")

        if not value:
            continue

        # Allow to have lists as values in the tool data
        if isinstance(value, (list, tuple)):
            value = ";".join(value)

        result[variable] = value

    return result


def append(env, env_b):
    """Append paths of environment b into environment"""
    # todo: should this be refactored to "join" or "extend"
    # todo: this function name might also be confusing with "merge"
    env = env.copy()
    for variable, value in env_b.items():
        for path in value.split(";"):
            if not path:
                continue

            lib.append_path(env, variable, path)

    return env


def get_tools(tools, platform_name=None):
    """Return combined environment for the given set of tools.

    This will find merge all the required environment variables of the input
    tools into a single dictionary. Then it will do a recursive format to
    format all dynamic keys and values using the same dictionary. (So that
    tool X can rely on variables of tool Y).

    Examples:
        get_environment(["maya2018", "yeti2.01", "mtoa2018"])
        get_environment(["global", "fusion9", "ofxplugins"])

    Args:
        tools (list): List of tool names.
        platform_name (str, Optional): The name of the platform to retrieve
            for. This defaults to the current platform you're running on.
            Possible values are: "darwin", "linux", "windows"

    Returns:
        dict: The environment required for the tools.

    """

    try:
        env_paths = os.environ['TOOL_ENV'].split(os.pathsep)
    except KeyError:
        raise KeyError(
            '"TOOL_ENV" environment variable not found. '
            'Please create it and point it to a folder with your .json '
            'config files.'
         )

    # Collect the tool files to load
    tool_paths = []
    for env_path in env_paths:
        for tool in tools:
            tool_paths.append(os.path.join(env_path, tool + ".json"))

    environment = dict()
    for tool_path in tool_paths:

        # Load tool
        try:
            with open(tool_path, "r") as f:
                tool_env = json.load(f)
            log.debug('Read tool successfully: {}'.format(tool_path))
        except IOError:
            log.debug(
                'Unable to find the environment file: "{}"'.format(tool_path)
            )
            continue
        except ValueError as e:
            log.debug(
                'Unable to read the environment file: "{0}", due to:'
                '\n{1}'.format(tool_path, e)
            )
            continue

        tool_env = parse(tool_env, platform_name=platform_name)
        environment = append(environment, tool_env)

    return environment


def merge(env, current_env):
    """Merge the tools environment with the 'current_env'.

    This finalizes the join with a current environment by formatting the
    remainder of dynamic variables with that from the current environment.

    Remaining missing variables result in an empty value.

    Args:
        env (dict): The dynamic environment
        current_env (dict): The "current environment" to merge the dynamic
            environment into.

    Returns:
        dict: The resulting environment after the merge.

    """

    result = current_env.copy()
    for key, value in env.items():
        value = lib.partial_format(value, data=current_env, missing="")
        result[key] = value

    return result

