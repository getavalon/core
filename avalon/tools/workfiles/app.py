import sys
import os
import tempfile
import subprocess
import getpass
import re


from ...vendor.Qt import QtWidgets, QtCore
from ... import style
from avalon import io


def determine_application(executable):
        # Determine executable
        application = None

        basename = os.path.basename(executable).lower()

        if "maya" in basename:
            application = "maya"

        if "nuke" in basename:
            application = "nuke"

        if "python" in basename:
            application = "python"

        if application is None:
            raise ValueError(
                "Could not determine application from executable:"
                " \"{0}\"".format(executable)
            )

        return application


class NewFileWindow(QtWidgets.QDialog):
    """New File Window"""

    def __init__(self, executable, root):
        super(NewFileWindow, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.setup(root, executable)
        self.update_work_file()

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        label = QtWidgets.QLabel("Version:")
        self.layout.addWidget(label, 0, 0)
        self.version_spinbox = QtWidgets.QSpinBox()
        self.version_spinbox.setMinimum(1)
        self.version_spinbox.setMaximum(9999)
        # Since the version can be padded with "{version:0>4}" we only search
        # for "{version".
        if "{version" not in self.template:
            label.setVisible(False)
            self.version_spinbox.setVisible(False)
        self.layout.addWidget(self.version_spinbox, 0, 1)

        label = QtWidgets.QLabel("Comment:")
        self.layout.addWidget(label, 1, 0)
        self.comment_lineedit = QtWidgets.QLineEdit()
        if "{comment}" not in self.template:
            label.setVisible(False)
            self.comment_lineedit.setVisible(False)
        self.layout.addWidget(self.comment_lineedit, 1, 1)

        self.label = QtWidgets.QLabel("File name")
        self.layout.addWidget(self.label, 2, 0)
        self.update_label()

        self.create_button = QtWidgets.QPushButton("Create")
        self.layout.addWidget(self.create_button, 3, 0)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.layout.addWidget(self.cancel_button, 3, 1)

        self.version_spinbox.valueChanged.connect(self.on_version_changed)
        self.comment_lineedit.textChanged.connect(self.on_comment_changed)
        self.create_button.pressed.connect(self.on_create_pressed)
        self.cancel_button.pressed.connect(self.on_cancel_pressed)

    def on_comment_changed(self, text):
        self.data["comment"] = text
        self.update_work_file()
        self.update_label()

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
        data = self.data.copy()
        template = self.template

        if not data["comment"]:
            data.pop("comment", None)

        # Remove optional missing keys
        pattern = re.compile(r"<.*?>")
        invalid_optionals = []
        for group in pattern.findall(template):
            try:
                group.format(**data)
            except KeyError:
                invalid_optionals.append(group)

        for group in invalid_optionals:
            template = template.replace(group, "")

        work_file = template.format(**data)

        # Remove optional symbols
        work_file = work_file.replace("<", "")
        work_file = work_file.replace(">", "")

        self.work_file = work_file + self.extensions[self.application]

    def update_label(self):
        self.label.setText(
            "<font color='green'>{0}</font>".format(self.work_file)
        )
        if os.path.exists(os.path.join(self.root, self.work_file)):
            self.label.setText(
                "<font color='red'>Cannot create \"{0}\" because file exists!"
                "</font>".format(self.work_file)
            )

    def on_version_changed(self, value):
        self.data["version"] = value
        self.update_work_file()
        self.update_label()

    def on_cancel_pressed(self):
        self.close()

    def setup(self, root, executable):
        self.executable = executable
        self.root = root
        self.application = determine_application(executable)

        # Need Mayapy for generating work files. Assuming maya and mayapy
        # executable are in the same directory.
        if self.application == "maya":
            self.executable = os.path.join(
                os.path.dirname(executable),
                os.path.basename(executable).replace("maya", "mayapy")
            )
            if not os.path.exists(executable):
                raise ValueError(
                    "Could not find Mayapy executable in \"{0}\"".format(
                        os.path.dirname(executable)
                    )
                )

        # Get work file name
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
            "version": 1,
            "user": getpass.getuser(),
            "comment": ""
        }

        self.template = "{task[name]}_v{version:0>4}<_{comment}>"
        templates = self.data["project"]["config"]["template"]
        if "workfile" in templates:
            self.template = templates["workfile"]

        self.extensions = {"maya": ".ma", "nuke": ".nk"}


class SaveFileWindow(NewFileWindow):
    """Save File Window"""

    def __init__(self, root, executable):
        super(SaveFileWindow, self).__init__(root, executable)

        self.create_button.setVisible(False)

        self.save_button = QtWidgets.QPushButton("Save")
        self.layout.addWidget(self.save_button, 3, 0)

        self.save_button.pressed.connect(self.on_save_pressed)

    def on_save_pressed(self):
        save = {"maya": self.save_maya}
        application = determine_application(sys.executable)
        if application not in save:
            raise ValueError(
                "Could not find a save method for this application."
            )

        file_path = os.path.join(self.root, self.work_file)
        save[application](file_path)

        self.close()

    def save_maya(self, file_path):
        from maya import cmds
        cmds.file(rename=file_path)
        cmds.file(save=True, type="mayaAscii")


class Window(QtWidgets.QDialog):
    """Work Files Window"""

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(kwargs["parent"])
        self.setWindowTitle("Work Files")

        self.work_file = None
        self.tempfile = kwargs["tempfile"]
        self.executable = kwargs["executable"]

        self.root = kwargs["root"]
        if self.root is None:
            self.root = os.getcwd()

        filters = {
            "maya": [".ma", ".mb"],
            "nuke": [".nk"]
        }
        application = determine_application(self.executable)
        self.filter = filters[application]

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.list = QtWidgets.QListWidget()
        self.layout.addWidget(self.list)
        self.refresh_list()

        buttons_layout = QtWidgets.QHBoxLayout()
        self.new_button = QtWidgets.QPushButton("New")
        buttons_layout.addWidget(self.new_button)
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.setVisible(False)
        buttons_layout.addWidget(self.save_button)
        self.open_button = QtWidgets.QPushButton("Open")
        buttons_layout.addWidget(self.open_button)
        self.browse_button = QtWidgets.QPushButton("Browse")
        buttons_layout.addWidget(self.browse_button)
        self.layout.addLayout(buttons_layout)

        # If within a host we need "Save" instead of "New"
        if determine_application(sys.executable) != "python":
            self.new_button.setVisible(False)
            self.save_button.setVisible(True)

        self.new_button.pressed.connect(self.on_new_pressed)
        self.save_button.pressed.connect(self.on_save_pressed)
        self.browse_button.pressed.connect(self.on_browse_pressed)
        self.open_button.pressed.connect(self.on_open_pressed)

        self.open_button.setFocus()

    def refresh_list(self):
        self.list.clear()
        items = []
        modified = []
        for f in os.listdir(self.root):
            if os.path.isdir(os.path.join(self.root, f)):
                continue

            if self.filter and os.path.splitext(f)[1] not in self.filter:
                continue
            self.list.addItem(f)
            items.append(self.list.findItems(f, QtCore.Qt.MatchExactly)[0])
            modified.append(os.path.getmtime(os.path.join(self.root, f)))

        # Select last modified file
        if items:
            items[modified.index(max(modified))].setSelected(True)

        self.list.setMinimumWidth(self.list.sizeHintForColumn(0) + 30)

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

    def on_save_pressed(self):
        window = SaveFileWindow(self.executable, self.root)
        window.setStyleSheet(style.load_stylesheet())
        window.exec_()

        self.close()

    def on_open_pressed(self):
        self.work_file = os.path.join(
            self.root, self.list.selectedItems()[0].text()
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

    return work_file


def cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        help="Work directory. Example: --root /path/to/work/directory"
    )
    parser.add_argument(
        "--executable",
        help="Executable to create new files from. "
        "Example: --executable /path/to/maya"
    )

    kwargs, args = parser.parse_known_args(sys.argv)

    show(**vars(kwargs))
