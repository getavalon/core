
import re
from ..vendor.Qt import QtWidgets, QtGui


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


class Bool(InputBase):
    """Option box input widget for `bool` type value

    Args:
        name (str): Value entry name, also taken as widget label
        default (bool, optional): Default false
        help (str, optional): Widget tool tip

    """

    def __init__(self, name, default=False, help=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        help = help or ""

        input = QtWidgets.QCheckBox(nice_naming(name))
        input.setToolTip(help)
        if default:
            input.setChecked()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(input)

        self.layout = layout
        self.key = name
        self.tip = help
        self.input = input

    def get(self):
        return self.input.isChecked()


class Int(InputBase):
    """Option box input widget for `int` type value

    Args:
        name (str): Value entry name, also taken as widget label
        default (int, optional): Default 0
        min (int, optional): Minimum input value, default 0
        max (int, optional): Maximum input value, default 99
        help (str, optional): Widget tool tip

    """

    def __init__(self, name, default=0, min=0, max=99, help=None, parent=None):
        InputBase.__init__(self, name, help, parent)

        input = QtWidgets.QSpinBox()
        input.setValue(default)
        input.setMinimum(min)
        input.setMaximum(max)

        self.layout.addWidget(input)
        self.input = input

    def get(self):
        return self.input.value()


def line_edit_float(default=0.0):
    """Return a QLineEdit widget for inputting float value

    Args:
        default (float, optional): Default 0.0

    """
    widget = QtWidgets.QLineEdit()
    widget.setValidator(QtGui.QDoubleValidator())
    widget.setText(str(float(default)))
    return widget


class Float(InputBase):
    """Option box input widget for `float` type value

    Args:
        name (str): Value entry name, also taken as widget label
        default (float, optional): Default 0.0
        help (str, optional): Widget tool tip

    """

    def __init__(self, name, default=0.0, help=None, parent=None):
        InputBase.__init__(self, name, help, parent)

        input = line_edit_float(default)

        self.layout.addWidget(input)
        self.input = input

    def get(self):
        return float(self.input.text())


class Double3(InputBase):
    """Option box input widget for array of three doubles

    Args:
        name (str): Value entry name, also taken as widget label
        default (tuple or list, optional): Default (0.0, 0.0, 0.0)
        help (str, optional): Widget tool tip

    """

    def __init__(self, name, default=None, help=None, parent=None):
        default = default or (0.0, 0.0, 0.0)
        assert isinstance(default, (list, tuple)), "Should be list or tuple."
        assert len(default) == 3, "Should have exact three elements."

        InputBase.__init__(self, name, help, parent)

        input = QtWidgets.QWidget()

        x, y, z = (line_edit_float(v) for v in default)

        layout = QtWidgets.QHBoxLayout(input)
        layout.addWidget(x)
        layout.addWidget(y)
        layout.addWidget(z)

        self.layout.addWidget(input)
        self.inputs = (x, y, z)

    def get(self):
        return tuple(float(i.text()) for i in self.inputs)


class String(InputBase):
    """Option box input widget for `str` type value

    Args:
        name (str): Value entry name, also taken as widget label
        default (str, optional): Default None
        placeholder (str, optional): Widget placeholder text, default None
        help (str, optional): Widget tool tip

    """

    def __init__(self,
                 name,
                 default=None,
                 placeholder=None,
                 help=None,
                 parent=None):
        InputBase.__init__(self, name, help, parent)

        input = QtWidgets.QLineEdit()
        input.setPlaceholderText(placeholder or "")
        input.setText(default or "")

        self.layout.addWidget(input)
        self.input = input

    def get(self):
        return self.input.text()


class GetOne(InputBase):
    """Option box input widget for selecting one value from a list

    Args:
        name (str): Value entry name, also taken as widget label
        elements (list): A list of values to select from
        default (int, optional): Index for default value from list, default 0
        as_string (bool, optional): Return as index or string, default true
        help (str, optional): Widget tool tip

    """

    def __init__(self,
                 name,
                 elements,
                 default=0,
                 as_string=True,
                 help=None,
                 parent=None):
        InputBase.__init__(self, name, help, parent)

        input = QtWidgets.QComboBox()
        input.addItems(elements)
        input.setCurrentIndex(default)

        self.layout.addWidget(input)
        self.input = input
        self.as_string = as_string

    def get(self):
        if self.as_string:
            return self.input.currentText()
        else:
            return self.input.currentIndex()
