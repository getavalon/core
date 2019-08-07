"""Initialize the avalon style."""
import logging
import platform
import os

from ..vendor.Qt import (
    QtCore,
    QtGui,
    __binding__
)

from . import colors

_log = logging.getLogger("avalon.style")


def load_stylesheet():
    """Loads the stylesheet.

    This takes care of importing the rc module for the correct binding loaded
    with Qt.py.

    Returns:
        str: The Stylesheet string.

    """

    # Smart import of the rc file
    if __binding__ == "PySide":
        from . import pyside_style_rc
    elif __binding__ == "PyQt4":
        from . import pyqt_style_rc
    elif __binding__ == "PySide2":
        from . import pyside_style_rc
    elif __binding__ == "PyQt5":
        from . import pyqt5_style_rc
    else:
        RuntimeError("Unsupported Qt binding: {0}".format(__binding__))

    # Load the fonts
    _load_fonts()

    # Load the stylesheet content from resources
    path = os.path.join(os.path.dirname(__file__), "style.qss")
    if not os.path.exists(path):
        _log.error("Unable to load stylesheet, file not found in resources")
        return ""

    with open(path, "r") as f:
        stylesheet = f.read()

        # fix bug on mac os; see cbdarkstyle issue #12 on github
        if platform.system().lower() == 'darwin':
            mac_fix = '''
            QDockWidget::title
            {
                background-color: #353434;
                text-align: center;
                height: 12px;
            }
            '''
            stylesheet += mac_fix

    return stylesheet


def _load_fonts():
    """Load the fonts.

    This will add the OpenSans fonts to the QFontDatabase.

    Returns:
        list: The registered font ids.

    """

    font_root = os.path.join(os.path.dirname(__file__), "fonts")
    fonts = [
        "opensans/OpenSans-Bold.ttf",
        "opensans/OpenSans-BoldItalic.ttf",
        "opensans/OpenSans-ExtraBold.ttf",
        "opensans/OpenSans-ExtraBoldItalic.ttf",
        "opensans/OpenSans-Italic.ttf",
        "opensans/OpenSans-Light.ttf",
        "opensans/OpenSans-LightItalic.ttf",
        "opensans/OpenSans-Regular.ttf",
        "opensans/OpenSans-Semibold.ttf",
        "opensans/OpenSans-SemiboldItalic.ttf",
    ]

    for font in fonts:
        path = os.path.join(font_root, font)
        QtGui.QFontDatabase.addApplicationFont(path)
