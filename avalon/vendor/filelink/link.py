import os
import platform


HARDLINK = 0


def _create_windows(source, destination, link_type):
    """Creates hardlink at destination from source in Windows."""

    if link_type == HARDLINK:
        import ctypes
        from ctypes.wintypes import BOOL
        CreateHardLink = ctypes.windll.kernel32.CreateHardLinkW
        CreateHardLink.argtypes = [
            ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_void_p
        ]
        CreateHardLink.restype = BOOL

        res = CreateHardLink(destination, source, None)
        if res == 0:
            raise ctypes.WinError()
    else:
        raise NotImplementedError("Link type unrecognized.")


def _create_linux(source, destination, link_type):
    """Creates hardlink at destination from source in Linux."""

    if link_type == HARDLINK:
        os.link(source, destination)
    else:
        raise NotImplementedError("Link type unrecognized.")


def _create_osx(source, destination, link_type):
    """Creates hardlink at destination from source in OSX."""
    # OSX is not supported yet, as testing on Travis does not support Python
    # natively.
    raise NotImplementedError("OSX is not support yet.")


def create(source, destination, link_type=HARDLINK):
    """Creates a hardlink at destination referring to the same file."""

    system = platform.system()

    if system == "Windows":
        _create_windows(source, destination, link_type)
    elif system == "Linux":
        _create_linux(source, destination, link_type)
    elif system == "Darwin":
        _create_osx(source, destination, link_type)
    else:
        raise NotImplementedError(
            "Unsupported platform: \"{0}\"".format(system)
        )
