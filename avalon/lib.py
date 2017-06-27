"""Helper functions"""

import logging
import datetime

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
