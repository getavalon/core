
import re
from ..vendor.Qt import QtWidgets


def nice_naming(key):
    """Convert camelCase name into UI Display Name"""
    words = re.findall('[A-Z][^A-Z]*', key[0].upper() + key[1:])
    return " ".join(words)


class InputBase(QtWidgets.QWidget):
    """Base class of option box input widgets (value type oriented)"""

    def __init__(self, name, help=None, parent=None):
        super(InputBase, self).__init__(parent=parent)
        help = help or ""

        label = QtWidgets.QLabel(nice_naming(name))
        label.setToolTip(help)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)

        self.layout = layout
        self.key = name
        self.tip = help

    def link(self, slot):
        """Internal use. Connecting widget to option dialog"""
        slot[self.key] = self

    def get(self):
        """Method for returning value from input widget"""
        raise NotImplementedError("Should be implemented in subclass.")
