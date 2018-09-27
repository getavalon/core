#!/bin/env python
# Copyright (c) 2013, Asi Soudai - www.asimation.com
# All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#

"""
Wrapper above built-in python logging module to help logging to Shell, Maya and Nuke
directly using timestamp and logging-level to keep the logs clean.

Also, both Maya and Nuke have specific handlers that allow application sepcific logging
using warning and popup messages that are native to those applications.
fatal and critical levels will pop a warning message in Nuke and Maya to make sure
user attention was grabbed when needed.

To use:
    log = getLogger( 'mylogger' )
    log.info( 'log something' )

    # Set level to debug
    log = getLogger( 'mylogger', level=DEBUG )
    # OR
    log = getLogger( 'mylogger' )
    log.setLevel( DEBUG )

    # Alart user:
    try:
        ... do something
    except Exception, error :
        log.fatal( "pop up this message if we're in nuke or maya" )
        raise error # re raise the error after we msg the user.
"""

# -----------------------------------------------------------------------------
#   Imports
# -----------------------------------------------------------------------------
import sys
import logging

# Load Maya:
try:
    import maya
    _in_maya = True
except Exception:
    _in_maya = False

# Load Nuke:
try:
    import nuke
    _in_nuke = True
except Exception:
    _in_nuke = False


# Load Nuke:
try:
    import nuke
    _in_nuke = True
except Exception:
    _in_nuke = False

# Load Mobu:
try:
    import pyfbsdk
    _in_mobu = True
except Exception:
    _in_mobu = False

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


# -----------------------------------------------------------------------------
# getLogger - Main Call
# -----------------------------------------------------------------------------
def getLogger(
    name,
    shell=True,
    maya=_in_maya,
    nuke=_in_nuke,
    mobu=_in_mobu,
    file=None,
    level=INFO
):
    '''
    Get logger - mimicing the usage of logging.getLogger()
            name(str) : logger name
            shell(bol): output to shell
            maya(bol) : output to maya editor
            nuke(bol) : output to nuke editor
            file(str) : output to given filename
            level(int): logger level
    '''
    return Logger(name, shell, maya, nuke, mobu, file, level)


# -----------------------------------------------------------------------------
# Logger Class
# -----------------------------------------------------------------------------
class Logger():
    '''
    '''

    def __init__(
        self,
        name,
        shell=True,
        maya=False,
        nuke=False,
        mobu=False,
        file=None,
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

        # Shell:
        if shell:
            stream_hdlr = ShellHandler()
            stream_hdlr.setFormatter(format)
            self.__logger.addHandler(stream_hdlr)

        # File:
        if file:
            file_hdlr = logging.FileHandler(file)
            file_hdlr.setFormatter(format)
            self.__logger.addHandler(file_hdlr)

        # Maya:
        if maya and _in_maya:
            maya_hdlr = MayaHandler()
            maya_hdlr.setFormatter(format)
            self.__logger.addHandler(maya_hdlr)

        # Nuke:
        if nuke and _in_nuke:
            nuke_hdlr = NukeHandler()
            nuke_hdlr.setFormatter(format)
            self.__logger.addHandler(nuke_hdlr)

        # Mobu:
        if mobu and _in_mobu:
            mobu_hdlr = MobuHandler()
            mobu_hdlr.setFormatter(format)
            self.__logger.addHandler(mobu_hdlr)

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


# -----------------------------------------------------------------------------
# ShellHandler
# -----------------------------------------------------------------------------
class ShellHandler(logging.Handler):
    '''
    Shell Handler - emits logs to shell only.
    by passing maya and nuke editors by using sys.__stdout__
    '''

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):

        try:
            sys.__stdout__.write("%s\n" % self.format(record))
        except IOError:
            # MotionBuilder is doing something funky with python,
            # so sometimes ( not always ) is blocked from writting:
            sys.stdout.write("%s\n" % self.format(record))


# -----------------------------------------------------------------------------
# MayaHandler
# -----------------------------------------------------------------------------
class MayaHandler(logging.Handler):
    '''
    Maya Handler - emits logs into maya's script editor.
    warning will emit maya.cmds.warning()
    critical and fatal would popup msg dialog to alert of the error.
    '''

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):

        # Formated message:
        msg = self.format(record)

        if record.funcName == "warning":
            maya.cmds.warning("\n"+msg)

        elif record.funcName in ["critical", "fatal"]:

            # Emit stdout print:
            sys.stdout.write("\n"+msg+"\n")

            # Open dialog if not in batch mode:
            if maya.cmds.about(batch=True) is False:

                maya.cmds.confirmDialog(
                    title="A {} have accure".format(
                        record.funcName
                    ),
                    message=record.message,
                    button=['Dismiss'],
                    messageAlign="left")

        else:
            sys.stdout.write(msg+"\n")


# -----------------------------------------------------------------------------
# NukeHandler
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# MobuHandler
# -----------------------------------------------------------------------------


class MobuHandler(logging.Handler):
    '''
    MotionBuilder Handler - emits logs into motionbuilder's script editor.
    '''

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):

        # Formated message:
        msg = self.format(record)

        if record.funcName == "warning":
            sys.stdout.write(msg+"\n")

        elif record.funcName == "error":
            sys.stderr.write(msg+"\n")

        elif record.funcName in ["critical", "fatal"]:
            FBMessageBox(record.funcName, msg, "OK")
            sys.stderr.write(msg+"\n")

        else:
            sys.stdout.write(msg+"\n")


# -----------------------------------------------------------------------------
# __name__
# -----------------------------------------------------------------------------
if __name__ == '__main__':

    log = getLogger("logger_name", shell=True)
    log.setLevel(logging.DEBUG)
    log.debug('debug msg')
    log.info('info msg')
    log.warning('warning msg')
    log.fatal('fatal msg')
