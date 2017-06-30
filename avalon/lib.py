"""Helper functions"""

import os
import json
import logging
import datetime

from . import schema
from .vendor import six, toml

logging.basicConfig()
logger = logging.getLogger("avalon")

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


def get_application(name, environment):
    application_definition = which_app(name)

    if application_definition is None:
        raise ValueError(
            "No application definition could be found for '%s'" % name
        )

    try:
        with open(application_definition) as f:
            app = toml.load(f)
            logger.debug(json.dumps(app, indent=4))
            schema.validate(app, "application")
    except (schema.ValidationError,
            schema.SchemaError,
            toml.TomlDecodeError) as e:
        logger.error("%s was invalid." % application_definition)
        raise

    executable = which("mayapy")

    if executable is None:
        raise ValueError(
            "'%s' not found on your PATH\n%s"
            % (app["executable"], os.getenv("PATH"))
        )

    try:
        app = dict_format(app, **environment)
    except KeyError as e:
        logger.error(
            "One of the {variables} defined in the application "
            "definition wasn't found in this session.\n"
            "The variable was %s " % e
        )
        logger.error(json.dumps(environment, indent=4, sort_keys=True))

        raise ValueError(
            "This is typically a bug in the pipeline, "
            "ask your developer.")

    # Ingest application environment
    environment = app.get("environment", {})
    for key, value in environment.copy().items():
        if isinstance(value, list):
            # Treat list values as paths, e.g. PYTHONPATH=[]
            environment[key] = os.pathsep.join(value)

        elif isinstance(value, str):
            environment[key] = value

        else:
            logger.error(
                "%s: Unsupported environment reference in %s"
                % (value, name)
            )

    return app
