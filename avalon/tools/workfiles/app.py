import sys
import os
import tempfile


from ...vendor.Qt import QtWidgets
from ... import style


class Window(QtWidgets.QDialog):
    """Work Files Window"""

    def __init__(self, temp, root, parent, filter):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Work Files")
        self.tempfile = temp
        self.filter = filter
        self.root = root
        if root is None:
            self.root = os.getcwd()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.list = QtWidgets.QListWidget()
        self.layout.addWidget(self.list)
        self.items = {}
        count = 0
        for f in os.listdir(self.root):
            if filter and os.path.splitext(f)[1] not in filter:
                continue
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

        self.browse_button.pressed.connect(self.on_browse_pressed)
        self.open_button.pressed.connect(self.on_open_pressed)

    def write_data(self):
        self.tempfile.write(self.work_file.replace("\\", "/"))
        self.close()

    def on_open_pressed(self):
        self.work_file = os.path.join(
            self.root, self.list.currentItem().text()
        )

        self.write_data()

    def on_browse_pressed(self):

        filter = " *".join(self.filter)
        filter = "Work File (*{0})".format(filter)

        self.work_file = QtWidgets.QFileDialog.getOpenFileName(
            caption="Work Files",
            directory=self.root,
            filter=filter
        )[0]

        self.write_data()


def show(root=None, parent=None, filter=[]):
    """Show Work Files GUI"""
    temp = tempfile.TemporaryFile(mode="w+t")

    app = QtWidgets.QApplication.instance()

    if not app:
        print("Starting new QApplication..")
        app = QtWidgets.QApplication(sys.argv)
        window = Window(temp, root, parent, filter)
        window.setStyleSheet(style.load_stylesheet())
        window.show()
        app.exec_()
    else:
        print("Using existing QApplication..")
        window = Window(temp, root, parent, filter)
        window.setStyleSheet(style.load_stylesheet())
        window.exec_()

    temp.seek(0)
    work_file = temp.read()
    temp.close()

    print(work_file)
    return work_file


def cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        help="Work directory. Example: --root /path/to/work/directory"
    )
    parser.add_argument(
        "--filter",
        action="append",
        help="Filters to show files with. Example: --filter .ma"
    )

    kwargs, args = parser.parse_known_args(sys.argv)

    show(**vars(kwargs))
