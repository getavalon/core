import sys
import os
import tempfile
import subprocess


from ...vendor.Qt import QtWidgets, QtCore
from ... import style
from avalon import io, lib


class NewFileWindow(QtWidgets.QDialog):
    """Work Files Window"""

    def __init__(self, executable, root):
        super(NewFileWindow, self).__init__()
        self.setWindowTitle("New File")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.executable = executable
        self.root = root
        self.setup()
        self.update_work_file()

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        label = QtWidgets.QLabel("Version:")
        self.layout.addWidget(label, 0, 0)
        self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setMinimum(1)
        self.layout.addWidget(self.spinbox, 0, 1)

        self.label = QtWidgets.QLabel("File name")
        self.layout.addWidget(self.label, 1, 0)
        self.update_label()

        self.create_button = QtWidgets.QPushButton("Create")
        self.layout.addWidget(self.create_button, 2, 0)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.layout.addWidget(self.cancel_button, 2, 1)

        self.spinbox.valueChanged.connect(self.on_spinbox_valuechange)
        self.create_button.pressed.connect(self.on_create_pressed)
        self.cancel_button.pressed.connect(self.on_cancel_pressed)

    def on_create_pressed(self):
        file_path = os.path.join(self.root, self.work_file)

        if os.path.exists(file_path):
            raise ValueError(
                "File already exists at: \"{0}\"".format(file_path)
            )

        scripts = {
            "maya": os.path.abspath(
                os.path.join(__file__, "..", "maya_workfile.py")
            ),
            "nuke": os.path.abspath(
                os.path.join(__file__, "..", "nuke_workfile.py")
            )
        }

        # For some reason Nuke does not block when using subprocess.call so the
        # work files list updates before the new file is created.
        # subprocess.check_output seems to fix this issue.
        subprocess.check_output(
            [
                "python",
                scripts[self.application],
                self.executable,
                file_path
            ]
        )

        self.close()

    def update_work_file(self):
        self.data["version"] = self.version
        self.work_file = self.template.format(**self.data)
        self.work_file += self.extensions[self.application]

    def update_label(self):
        self.label.setText(self.work_file)
        if os.path.exists(os.path.join(self.root, self.work_file)):
            self.label.setText(
                "<font color='red'>Cannot create \"{0}\" because file exists!"
                "</font>".format(self.work_file)
            )

    def on_spinbox_valuechange(self, value):
        self.version = value
        self.update_work_file()
        self.update_label()

    def on_cancel_pressed(self):
        self.close()

    def setup(self):
        # Determine executable
        self.application = None

        if "maya" in os.path.basename(self.executable).lower():
            self.application = "maya"
            # Need Mayapy for generating work files. Assuming maya and mayapy
            # executable are in the same directory.
            self.executable = os.path.join(
                os.path.dirname(self.executable),
                os.path.basename(self.executable).replace("maya", "mayapy")
            )
            if not os.path.exists(self.executable):
                raise ValueError(
                    "Could not find Mayapy executable in \"{0}\"".format(
                        os.path.dirname(self.executable)
                    )
                )

        if "nuke" in os.path.basename(self.executable).lower():
            self.application = "nuke"

        if self.application is None:
            raise ValueError(
                "Could not determine executable: \"{0}\"".format(
                    self.executable
                )
            )

        # Get work file name
        self.version = 1
        self.data = {
            "project": io.find_one(
                {"name": os.environ["AVALON_PROJECT"], "type": "project"}
            ),
            "asset": io.find_one(
                {"name": os.environ["AVALON_ASSET"], "type": "asset"}
            ),
            "task": {
                "name": os.environ["AVALON_TASK"].lower(),
                "label": os.environ["AVALON_TASK"]
            },
            "version": self.version
        }

        self.template = "{task[name]}_v{version:0>4}"
        templates = self.data["project"]["config"]["template"]
        if "workfile" in templates:
            self.template = templates["workfile"]

        self.extensions = {"maya": ".ma", "nuke": ".nk"}


class Window(QtWidgets.QDialog):
    """Work Files Window"""

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(kwargs["parent"])
        self.setWindowTitle("Work Files")
        self.work_file = None

        self.tempfile = kwargs["tempfile"]
        self.filter = kwargs["filter"]

        self.executable = kwargs["executable"]

        self.root = kwargs["root"]
        if self.root is None:
            self.root = os.getcwd()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.list = QtWidgets.QListWidget()
        self.layout.addWidget(self.list)
        self.refresh_list()

        buttons_layout = QtWidgets.QHBoxLayout()
        self.new_button = QtWidgets.QPushButton("New")
        buttons_layout.addWidget(self.new_button)
        self.open_button = QtWidgets.QPushButton("Open")
        buttons_layout.addWidget(self.open_button)
        self.browse_button = QtWidgets.QPushButton("Browse")
        buttons_layout.addWidget(self.browse_button)
        self.layout.addLayout(buttons_layout)

        self.new_button.pressed.connect(self.on_new_pressed)
        self.browse_button.pressed.connect(self.on_browse_pressed)
        self.open_button.pressed.connect(self.on_open_pressed)

    def refresh_list(self):
        self.list.clear()
        self.items = {}
        count = 0
        for f in os.listdir(self.root):
            if os.path.isdir(os.path.join(self.root, f)):
                continue

            if self.filter and os.path.splitext(f)[1] not in self.filter:
                continue
            self.list.addItem(f)
            self.items[f] = count
            count += 1

    def write_data(self):
        self.tempfile.write(self.work_file.replace("\\", "/"))
        self.close()

    def on_new_pressed(self):
        if not self.executable:
            raise ValueError(
                "No executable specified for work file creation."
            )

        window = NewFileWindow(self.executable, self.root)
        window.setStyleSheet(style.load_stylesheet())
        window.exec_()

        self.refresh_list()

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


def show(parent=None, **kwargs):
    """Show Work Files GUI"""
    temp = tempfile.TemporaryFile(mode="w+t")

    app = QtWidgets.QApplication.instance()

    kwargs["parent"] = parent
    kwargs["tempfile"] = temp

    if "root" not in kwargs:
        kwargs["root"] = None

    if "filter" not in kwargs:
        kwargs["filter"] = []

    if "executable" not in kwargs:
        kwargs["executable"] = None

    if not app:
        print("Starting new QApplication..")
        app = QtWidgets.QApplication(sys.argv)
        window = Window(**kwargs)
        window.setStyleSheet(style.load_stylesheet())
        window.show()
        app.exec_()
    else:
        print("Using existing QApplication..")
        window = Window(**kwargs)
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
    parser.add_argument(
        "--executable",
        help="Executable to create new files from. "
        "Example: --executable /path/to/maya"
    )

    kwargs, args = parser.parse_known_args(sys.argv)

    show(**vars(kwargs))
