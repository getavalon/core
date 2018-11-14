import sys
import logging

import nuke

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
MSG_FORMAT = "%(asctime)s %(name)s %(levelname)s : %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# Levels - same as logging module
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0


def nuke_logger(
    name,
    level=INFO
):
    '''
    Get logger - mimicing the usage of logging.getLogger()
            name(str) : logger name
            level(int): logger level
    '''
    return Logger(name, level)


class Logger():

    def __init__(
        self,
        name,
        level=INFO
    ):
        '''
        Init Logger
        '''

        self.__name = name
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(level)

        # SafetyCheck - Don't create handelr if logger already have some.
        # this will prevent double handelrs creation.
        if self.__logger.handlers:
            return

        # Format
        format = logging.Formatter(MSG_FORMAT, DATE_FORMAT)

        nuke_hdlr = NukeHandler()
        nuke_hdlr.setFormatter(format)
        self.__logger.addHandler(nuke_hdlr)

    def __repr__(self):
        '''
        string representation.
        '''
        return "%s(%s Level:%i)" % (self.__class__, self.__name, self.level)

    def __getattr__(self, attr):
        '''
        Use logging.Logger attributes.
        '''
        if hasattr(self.__logger, attr):
            return getattr(self.__logger, attr)
        else:
            raise AttributeError("No attribute {}".format(attr))

    # LEVELS
    def debug(self, msg):
        self.__logger.debug(msg)

    def info(self, msg):
        self.__logger.info(msg)

    def warning(self, msg):
        self.__logger.warning(msg)

    def fatal(self, msg):
        self.__logger.fatal(msg)

    def critical(self, msg):
        self.__logger.critical(msg)


class NukeHandler(logging.Handler):
    '''
    Nuke Handler - emits logs into nuke's script editor.
    warning will emit nuke.warning()
    critical and fatal would popup msg dialog to alert of the error.
    '''

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):

        # Formated message:
        msg = self.format(record)

        if record.funcName == "warning":
            nuke.warning(msg)

        elif record.funcName in ["critical", "fatal"]:
            nuke.error(msg)
            nuke.message(record.message)

        else:
            sys.stdout.write(msg)
