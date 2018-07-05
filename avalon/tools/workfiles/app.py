import sys
import os


from ...vendor.Qt import QtWidgets
from ... import style
from .. import lib


class Window(QtWidgets.QDialog):
    """Work Files Window"""

    def __init__(self, root, parent):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Work Files")
        self.root = root

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.list = QtWidgets.QListWidget()
        self.layout.addWidget(self.list)
        self.items = {}
        count = 0
        for f in os.listdir(self.root):
            self.list.addItem(f)
            self.items[f] = count
            count += 1

        buttons_layout = QtWidgets.QHBoxLayout()
        self.new_button = QtWidgets.QPushButton("New")
        buttons_layout.addWidget(self.new_button)
        self.open_button = QtWidgets.QPushButton("Open")
        buttons_layout.addWidget(self.open_button)
        self.browse_button = QtWidgets.QPushButton("Browse")
        buttons_layout.addWidget(self.browse_button)
        self.layout.addLayout(buttons_layout)


def show(root=None, parent=None):
    """Show Work Files GUI"""

    with lib.application():
        window = Window(root, parent)
        window.setStyleSheet(style.load_stylesheet())
        window.show()


def cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Work directory.")

    kwargs, args = parser.parse_known_args(sys.argv)

    show(**vars(kwargs))
