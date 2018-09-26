import nuke
import logging
from .. import api, io
from pyblish import api as pyblish

MSG_FORMAT  = "%(asctime)s %(name)s %(levelname)s : %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Levels - same as logging module
CRITICAL = 50
FATAL    = CRITICAL
ERROR    = 40
WARNING  = 30
WARN     = WARNING
INFO     = 20
DEBUG    = 10
NOTSET   = 0

def containerise():
    """Bundle `nodes` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.
    """
    raise NotImplementedError(
        "\"containerise()\" has not been implemented for Nuke."
    )

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

    elif record.funcName in [ "critical", "fatal" ]:
        nuke.error(msg)
        nuke.message(record.message)

    else:
        sys.stdout.write(msg)

def getLogger( name, shell=True, file=None, level=INFO ):
	'''
	Get logger - mimicing the usage of logging.getLogger()
		name(str) : logger name
		shell(bol): output to shell
		maya(bol) : output to maya editor
		nuke(bol) : output to nuke editor
		file(str) : output to given filename
		level(int): logger level
	'''
	return Logger( name, shell, file, level )

def install(config):
    """Install Nuke-specific functionality of avalon-core.

    This is where you install menus and register families, data
    and loaders into Nuke.

    It is called automatically when installing via `api.install(nuke)`.

    See the Maya equivalent for inspiration on how to implement this.

    """
    _install_menu()
    _register_events()

    pyblish.register_host("nuke")

    # Remove all handlers associated with the root logger object, because
    # that one sometimes logs as "warnings" incorrectly.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Attach default logging handler that prints to active comp
    logger = logging.getLogger()
    formatter = logging.Formatter(fmt="%(message)s\n")
    handler = CompLogHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    __logger = logging.getLogger("logger_name")
    nuke_hdlr = NukeHandler()
    nuke_hdlr.setFormatter( logging.Formatter( MSG_FORMAT, DATE_FORMAT ) )
    __logger.addHandler( nuke_hdlr )

    # Trigger install on the config's "fusion" package
    try:
        config = importlib.import_module(config.__name__ + ".nuke")
    except ImportError:
        pass
    else:
        if hasattr(config, "install"):
            config.install()



def _uninstall_menu():
    menubar = nuke.menu("Nuke")
    menubar.removeItem(api.Session["AVALON_LABEL"])


def _install_menu():
    from ..tools import (
        creator,
        # publish,
        cbloader,
        cbsceneinventory,
        contextmanager
    )
    import pyblish_lite as publish

    # Create menu
    menubar = nuke.menu("Nuke")
    menu = menubar.addMenu(api.Session["AVALON_LABEL"])

    label = "{0}, {1}".format(
        api.Session["AVALON_ASSET"], api.Session["AVALON_TASK"]
    )
    context_menu = menu.addMenu(label)
    context_menu.addCommand("Set Context", contextmanager.show)

    menu.addSeparator()

    menu.addCommand("Create...", creator.show)
    menu.addCommand("Load...", cbloader.show)
    menu.addCommand("Publish...", publish.show)
    menu.addCommand("Manage...", cbsceneinventory.show)

    menu.addSeparator()

    menu.addCommand("Reset Frame Range", reset_frame_range)
    menu.addCommand("Reset Resolution", reset_resolution)


def reset_frame_range():
    """Set frame range to current asset"""
    fps = float(api.Session.get("AVALON_FPS", 25))

    nuke.root()["fps"].setValue(fps)

    asset = api.Session["AVALON_ASSET"]
    asset = io.find_one({"name": asset, "type": "asset"})

    try:
        edit_in = asset["data"]["edit_in"]
        edit_out = asset["data"]["edit_out"]
    except KeyError:
        print(
            "Frame range not set! No edit information found for "
            "\"{0}\".".format(asset["name"])
        )
        return

    nuke.root()["first_frame"].setValue(edit_in)
    nuke.root()["last_frame"].setValue(edit_out)


def reset_resolution():
    """Set resolution to project resolution."""
    project = io.find_one({"type": "project"})

    try:
        width = project["data"].get("resolution_width", 1920)
        height = project["data"].get("resolution_height", 1080)
    except KeyError:
        print(
            "No resolution information found for \"{0}\".".format(
                project["name"]
            )
        )
        return

    current_width = nuke.root()["format"].value().width()
    current_height = nuke.root()["format"].value().height()

    if width != current_width or height != current_height:

        fmt = None
        for f in nuke.formats():
            if f.width() == width and f.height() == height:
                fmt = f.name()

        if not fmt:
            nuke.addFormat(
                "{0} {1} {2}".format(int(width), int(height), project["name"])
            )
            fmt = project["name"]

        nuke.root()["format"].setValue(fmt)


def uninstall():
    """Uninstall all tha was installed

    This is where you undo everything that was done in `install()`.
    That means, removing menus, deregistering families and  data
    and everything. It should be as though `install()` was never run,
    because odds are calling this function means the user is interested
    in re-installing shortly afterwards. If, for example, he has been
    modifying the menu or registered families.

    """
    _uninstall_menu()

    pyblish.deregister_host("nuke")


def ls():
    """List available containers.

    This function is used by the Container Manager in Nuke. You'll
    need to implement a for-loop that then *yields* one Container at
    a time.

    See the `container.json` schema for details on how it should look,
    and the Maya equivalent, which is in `avalon.maya.pipeline`

    """
    raise NotImplementedError(
        "\"ls()\" has not been implemented for Nuke."
    )


def publish():
    """Shorthand to publish from within host"""
    import pyblish.util
    return pyblish.util.publish()


def _register_events():

    api.on("taskChanged", _on_task_changed)
    print("Installed event callback for 'taskChanged'..")


def _on_task_changed(*args):

    # Update menu
    _uninstall_menu()
    _install_menu()
