import sys
import os
import getpass
import re
import shutil

from ...vendor.Qt import QtWidgets, QtCore
from ... import style, io, api

from .. import lib as tools_lib


class NameWindow(QtWidgets.QDialog):
    """Name Window"""

    def __init__(self, root):
        super(NameWindow, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.result = None
        self.setup(root)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        grid_layout = QtWidgets.QGridLayout()

        label = QtWidgets.QLabel("Version:")
        grid_layout.addWidget(label, 0, 0)
        self.version_spinbox = QtWidgets.QSpinBox()
        self.version_spinbox.setMinimum(1)
        self.version_spinbox.setMaximum(9999)
        self.version_checkbox = QtWidgets.QCheckBox("Next Available Version")
        self.version_checkbox.setCheckState(QtCore.Qt.CheckState(2))
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.version_spinbox)
        layout.addWidget(self.version_checkbox)
        grid_layout.addLayout(layout, 0, 1)
        # Since the version can be padded with "{version:0>4}" we only search
        # for "{version".
        if "{version" not in self.template:
            label.setVisible(False)
            self.version_spinbox.setVisible(False)
            self.version_checkbox.setVisible(False)

        label = QtWidgets.QLabel("Comment:")
        grid_layout.addWidget(label, 1, 0)
        self.comment_lineedit = QtWidgets.QLineEdit()
        if "{comment}" not in self.template:
            label.setVisible(False)
            self.comment_lineedit.setVisible(False)
        grid_layout.addWidget(self.comment_lineedit, 1, 1)

        grid_layout.addWidget(QtWidgets.QLabel("Preview:"), 2, 0)
        self.label = QtWidgets.QLabel("File name")
        grid_layout.addWidget(self.label, 2, 1)

        self.layout.addLayout(grid_layout)

        layout = QtWidgets.QHBoxLayout()
        self.ok_button = QtWidgets.QPushButton("Ok")
        layout.addWidget(self.ok_button)
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        layout.addWidget(self.cancel_button)
        self.layout.addLayout(layout)

        self.version_spinbox.valueChanged.connect(
            self.on_version_spinbox_changed
        )
        self.version_checkbox.stateChanged.connect(
            self.on_version_checkbox_changed
        )
        self.comment_lineedit.textChanged.connect(self.on_comment_changed)
        self.ok_button.pressed.connect(self.on_ok_pressed)
        self.cancel_button.pressed.connect(self.on_cancel_pressed)

        # Allow "Enter" key to accept the save.
        self.ok_button.setDefault(True)

        # Force default focus to comment, some hosts didn't automatically
        # apply focus to this line edit (e.g. Houdini)
        self.comment_lineedit.setFocus()

        self.refresh()

    def on_version_spinbox_changed(self, value):
        self.data["version"] = value
        self.refresh()

    def on_version_checkbox_changed(self, value):
        self.refresh()

    def on_comment_changed(self, text):
        self.data["comment"] = text
        self.refresh()

    def on_ok_pressed(self):
        self.result = self.work_file.replace("\\", "/")
        self.close()

    def on_cancel_pressed(self):
        self.close()

    def get_result(self):
        return self.result

    def get_work_file(self, template=None):
        data = self.data.copy()
        template = template or self.template

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

        # Define saving file extension
        current_file = self.host.current_file()
        if current_file:
            # Match the extension of current file
            _, extension = os.path.splitext(current_file)
        else:
            # Fall back to the first extension supported for this host.
            extension = self.host.file_extensions()[0]

        work_file = work_file + extension

        return work_file

    def refresh(self):
        if self.version_checkbox.isChecked():
            self.version_spinbox.setEnabled(False)

            # Find matching files
            files = os.listdir(self.root)

            # Fast match on extension
            extensions = self.host.file_extensions()
            files = [f for f in files if os.path.splitext(f)[1] in extensions]

            # Build template without optionals, version to digits only regex
            # and comment to any definable value.
            # Note: with auto-increment the `version` key may not be optional.
            template = self.template
            template = re.sub("<.*?>", ".*?", template)
            template = re.sub("{version.*}", "([0-9]+)", template)
            template = re.sub("{comment.*?}", ".+?", template)
            template = self.get_work_file(template)
            template = "^" + template + "$"           # match beginning to end

            # Get highest version among existing matching files
            version = 1
            for file in sorted(files):
                match = re.match(template, file)
                if not match:
                    continue

                file_version = int(match.group(1))

                if file_version >= version:
                    version = file_version + 1

            self.data["version"] = version

            # safety check
            path = os.path.join(self.root, self.get_work_file())
            assert not os.path.exists(path), \
                "This is a bug, file exists: %s" % path

        else:
            self.version_spinbox.setEnabled(True)
            self.data["version"] = self.version_spinbox.value()

        self.work_file = self.get_work_file()

        self.label.setText(
            "<font color='green'>{0}</font>".format(self.work_file)
        )
        if os.path.exists(os.path.join(self.root, self.work_file)):
            self.label.setText(
                "<font color='red'>Cannot create \"{0}\" because file exists!"
                "</font>".format(self.work_file)
            )
            self.ok_button.setEnabled(False)
        else:
            self.ok_button.setEnabled(True)

    def setup(self, root):
        self.root = root
        self.host = api.registered_host()

        # Get work file name
        self.data = {
            "project": io.find_one(
                {"name": api.Session["AVALON_PROJECT"], "type": "project"}
            ),
            "asset": io.find_one(
                {"name": api.Session["AVALON_ASSET"], "type": "asset"}
            ),
            "task": {
                "name": api.Session["AVALON_TASK"].lower(),
                "label": api.Session["AVALON_TASK"]
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


class Window(QtWidgets.QDialog):
    """Work Files Window"""

    def __init__(self, root=None):
        super(Window, self).__init__()
        self.setWindowTitle("Work Files")
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.root = root

        if self.root is None:
            self.root = os.getcwd()

        self.host = api.registered_host()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Display current context
        # todo: context should update on update task
        label = u"<b>Asset</b> {0} \u25B6 <b>Task</b> {1}".format(
            api.Session["AVALON_ASSET"],
            api.Session["AVALON_TASK"]
        )
        self.context_label = QtWidgets.QLabel(label)
        self.context_label.setStyleSheet("QLabel{ font-size: 12pt; }")
        self.layout.addWidget(self.context_label)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Plain)
        self.layout.addWidget(separator)

        self.list = QtWidgets.QListWidget()
        self.layout.addWidget(self.list)

        buttons_layout = QtWidgets.QHBoxLayout()
        self.duplicate_button = QtWidgets.QPushButton("Duplicate")
        buttons_layout.addWidget(self.duplicate_button)
        self.open_button = QtWidgets.QPushButton("Open")
        buttons_layout.addWidget(self.open_button)
        self.browse_button = QtWidgets.QPushButton("Browse")
        buttons_layout.addWidget(self.browse_button)
        self.layout.addLayout(buttons_layout)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(separator)

        current_file = self.host.current_file()
        if current_file:
            current_label = os.path.basename(current_file)
        else:
            current_label = "<unsaved>"
        current_file_label = QtWidgets.QLabel("Current File: " + current_label)
        self.layout.addWidget(current_file_label)

        buttons_layout = QtWidgets.QHBoxLayout()
        self.save_as_button = QtWidgets.QPushButton("Save As")
        buttons_layout.addWidget(self.save_as_button)
        self.layout.addLayout(buttons_layout)

        self.duplicate_button.pressed.connect(self.on_duplicate_pressed)
        self.open_button.pressed.connect(self.on_open_pressed)
        self.list.doubleClicked.connect(self.on_open_pressed)
        self.browse_button.pressed.connect(self.on_browse_pressed)
        self.save_as_button.pressed.connect(self.on_save_as_pressed)

        self.open_button.setFocus()

        self.refresh()
        self.resize(400, 550)

    def get_name(self):
        window = NameWindow(self.root)
        window.setStyleSheet(style.load_stylesheet())
        window.exec_()

        return window.get_result()

    def refresh(self):
        self.list.clear()

        modified = []
        extensions = set(self.host.file_extensions())
        for f in sorted(os.listdir(self.root)):
            path = os.path.join(self.root, f)
            if os.path.isdir(path):
                continue

            if extensions and os.path.splitext(f)[1] not in extensions:
                continue

            self.list.addItem(f)
            modified.append(os.path.getmtime(path))

        # Select last modified file
        if self.list.count():
            item = self.list.item(modified.index(max(modified)))
            item.setSelected(True)

            # Scroll list so item is visible
            QtCore.QTimer.singleShot(100, lambda: self.list.scrollToItem(item))

            self.duplicate_button.setEnabled(True)
        else:
            self.duplicate_button.setEnabled(False)

        self.list.setMinimumWidth(self.list.sizeHintForColumn(0) + 30)

    def save_as_maya(self, file_path):
        from maya import cmds
        cmds.file(rename=file_path)
        cmds.file(save=True, type="mayaAscii")

    def save_as_nuke(self, file_path):
        import nuke
        nuke.scriptSaveAs(file_path)

    def save_changes_prompt(self):
        messagebox = QtWidgets.QMessageBox()
        messagebox.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        messagebox.setIcon(messagebox.Warning)
        messagebox.setWindowTitle("Unsaved Changes!")
        messagebox.setText(
            "There are unsaved changes to the current file."
            "\nDo you want to save the changes?"
        )
        messagebox.setStandardButtons(
            messagebox.Yes | messagebox.No | messagebox.Cancel
        )
        result = messagebox.exec_()

        if result == messagebox.Yes:
            return True
        elif result == messagebox.No:
            return False
        else:
            return None

    def open(self, filepath):
        host = self.host
        if host.has_unsaved_changes():
            result = self.save_changes_prompt()

            if result is None:
                # Cancel operation
                return False

            if result:
                # Save current scene, continue to open file
                host.save_file(host.current_file())

            else:
                # Don't save, continue to open file
                pass

        return host.open_file(filepath)

    def on_duplicate_pressed(self):
        work_file = self.get_name()

        if not work_file:
            return

        src = os.path.join(
            self.root, self.list.selectedItems()[0].text()
        )
        dst = os.path.join(
            self.root, work_file
        )
        shutil.copy(src, dst)

        self.refresh()

    def on_open_pressed(self):

        selection = self.list.selectedItems()
        if not selection:
            print("No file selected to open..")
            return

        work_file = os.path.join(self.root, selection[0].text())

        result = self.open(work_file)
        if result:
            self.close()

    def on_browse_pressed(self):

        filter = " *".join(self.host.file_extensions())
        filter = "Work File (*{0})".format(filter)
        work_file = QtWidgets.QFileDialog.getOpenFileName(
            caption="Work Files",
            dir=self.root,
            filter=filter
        )[0]

        if not work_file:
            self.refresh()
            return

        self.open(work_file)

        self.close()

    def on_save_as_pressed(self):
        work_file = self.get_name()

        if not work_file:
            return

        file_path = os.path.join(self.root, work_file)
        self.host.save_file(file_path)

        self.close()


def show(root=None, debug=False):
    """Show Work Files GUI"""

    host = api.registered_host()
    if host is None:
        raise RuntimeError("No registered host.")

    # Verify the host has implemented the api for Work Files
    required = ["open_file",
                "save_file",
                "current_file",
                "has_unsaved_changes",
                "work_root",
                "file_extensions",
                ]
    missing = []
    for name in required:
        if not hasattr(host, name):
            missing.append(name)
    if missing:
        raise RuntimeError("Host is missing required Work Files interfaces: "
                           "%s (host: %s)" % (", ".join(missing), host))

    # Allow to use a Host's default root.
    if root is None:
        root = host.work_root()
        if not root:
            raise ValueError("Root not given and no root returned by "
                             "default from current host %s" % host.__name__)

    if not os.path.exists(root):
        raise OSError("Root set for Work Files app does not exist: %s" % root)

    if debug:
        api.Session["AVALON_ASSET"] = "Mock"
        api.Session["AVALON_TASK"] = "Testing"

    with tools_lib.application():
        window = Window(root)
        window.setStyleSheet(style.load_stylesheet())

        if debug:
            # Enable closing in standalone
            window.show()

        else:
            # Cause modal dialog
            window.exec_()
