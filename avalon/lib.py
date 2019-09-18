"""Helper functions"""

import os
import sys
import json
import logging
import datetime
import subprocess
import types

from . import schema
from .vendor import six, toml

PY2 = sys.version_info[0] == 2

log_ = logging.getLogger(__name__)

# Backwards compatibility
logger = log_

__all__ = [
    "time",
    "log",
]


def time():
    """Return file-system safe string of current date and time"""
    return datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")


def log(cls):
    """Decorator for attaching a logger to the class `cls`

    Loggers inherit the syntax {module}.{submodule}

    Example
        >>> @log
        ... class MyClass(object):
        ...     pass
        >>>
        >>> myclass = MyClass()
        >>> myclass.log.info('Hello World')

    """

    module = cls.__module__
    name = cls.__name__

    # Package name appended, for filtering of LogRecord instances
    logname = "%s.%s" % (module, name)
    cls.log = logging.getLogger(logname)

    # All messages are handled by root-logger
    cls.log.propagate = True

    return cls


def dict_format(original, **kwargs):
    """Recursively format the values in *original* with *kwargs*.

    Example:
        >>> sample = {"key": "{value}", "sub-dict": {"sub-key": "sub-{value}"}}
        >>> dict_format(sample, value="Bob") == \
            {'key': 'Bob', 'sub-dict': {'sub-key': 'sub-Bob'}}
        True

    """

    new_dict = dict()
    new_list = list()

    if isinstance(original, dict):
        for key, value in original.items():
            if isinstance(value, dict):
                new_dict[key.format(**kwargs)] = dict_format(value, **kwargs)
            elif isinstance(value, list):
                new_dict[key.format(**kwargs)] = dict_format(value, **kwargs)
            elif isinstance(value, six.string_types):
                new_dict[key.format(**kwargs)] = value.format(**kwargs)
            else:
                new_dict[key.format(**kwargs)] = value

        return new_dict

    else:
        assert isinstance(original, list)
        for value in original:
            if isinstance(value, dict):
                new_list.append(dict_format(value, **kwargs))
            elif isinstance(value, list):
                new_list.append(dict_format(value, **kwargs))
            elif isinstance(value, six.string_types):
                new_list.append(value.format(**kwargs))
            else:
                new_list.append(value)

        return new_list


def which(program):
    """Locate `program` in PATH

    Arguments:
        program (str): Name of program, e.g. "python"

    """

    def is_exe(fpath):
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            return True
        return False

    for path in os.environ["PATH"].split(os.pathsep):
        for ext in os.getenv("PATHEXT", "").split(os.pathsep):
            fname = program + ext.lower()
            abspath = os.path.join(path.strip('"'), fname)

            if is_exe(abspath):
                return abspath

    return None


def which_app(app):
    """Locate `app` in PATH

    Arguments:
        app (str): Name of app, e.g. "python"

    """

    for path in os.environ["PATH"].split(os.pathsep):
        fname = app + ".toml"
        abspath = os.path.join(path.strip('"'), fname)

        if os.path.isfile(abspath):
            return abspath

    return None


def get_application(name):
    """Find the application .toml and parse it.

    Arguments:
        name (str): The name of the application to search.

    Returns:
        dict: The parsed application from the .toml settings.

    """
    application_definition = which_app(name)

    if application_definition is None:
        raise ValueError(
            "No application definition could be found for '%s'" % name
        )

    try:
        with open(application_definition) as f:
            app = toml.load(f)
            log_.debug(json.dumps(app, indent=4))
            schema.validate(app, "application")
    except (schema.ValidationError,
            schema.SchemaError,
            toml.TomlDecodeError) as e:
        log_.error("%s was invalid." % application_definition)
        raise

    return app


def launch(executable, args=None, environment=None, cwd=None):
    """Launch a new subprocess of `args`

    Arguments:
        executable (str): Relative or absolute path to executable
        args (list): Command passed to `subprocess.Popen`
        environment (dict, optional): Custom environment passed
            to Popen instance.

    Returns:
        Popen instance of newly spawned process

    Exceptions:
        OSError on internal error
        ValueError on `executable` not found

    """

    CREATE_NO_WINDOW = 0x08000000
    CREATE_NEW_CONSOLE = 0x00000010
    IS_WIN32 = sys.platform == "win32"
    PY2 = sys.version_info[0] == 2

    abspath = executable

    env = (environment or os.environ)

    if PY2:
        # Protect against unicode, and other unsupported
        # types amongst environment variables
        enc = sys.getfilesystemencoding()
        env = {k.encode(enc): v.encode(enc) for k, v in env.items()}

    kwargs = dict(
        args=[abspath] + args or list(),
        env=env,
        cwd=cwd,

        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,

        # Output `str` through stdout on Python 2 and 3
        universal_newlines=True,
    )

    if env.get("CREATE_NEW_CONSOLE"):
        kwargs["creationflags"] = CREATE_NEW_CONSOLE
        kwargs.pop("stdout")
        kwargs.pop("stderr")
    else:

        if IS_WIN32:
            kwargs["creationflags"] = CREATE_NO_WINDOW

    popen = subprocess.Popen(**kwargs)

    return popen


def modules_from_path(path):
    """Get python scripts as modules from a path.

    Arguments:
        path (str): Path to python scrips.

    Returns:
        List of modules.
    """

    path = os.path.normpath(path)

    if not os.path.isdir(path):
        log_.warning("%s is not a directory" % path)
        return []

    modules = []
    for fname in os.listdir(path):
        # Ignore files which start with underscore
        if fname.startswith("_"):
            continue

        mod_name, mod_ext = os.path.splitext(fname)
        if not mod_ext == ".py":
            continue

        abspath = os.path.join(path, fname)
        if not os.path.isfile(abspath):
            continue

        module = types.ModuleType(mod_name)
        module.__file__ = abspath

        try:
            with open(abspath) as f:
                six.exec_(f.read(), module.__dict__)

            # Store reference to original module, to avoid
            # garbage collection from collecting it's global
            # imports, such as `import os`.
            sys.modules[mod_name] = module

        except Exception as err:
            print("Skipped: \"%s\" (%s)", mod_name, err)
            continue

        modules.append(module)

    return modules
