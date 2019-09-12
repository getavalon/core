import sys
import os
import getpass
import re
import shutil
import logging

from ...vendor.Qt import QtWidgets, QtCore
from ...vendor import qtawesome
from ... import style, io, api

from .. import lib as tools_lib
from ..widgets import AssetWidget
from ..models import TasksModel

log = logging.getLogger(__name__)


class NameWindow(QtWidgets.QDialog):
    """Name Window to define a unique filename inside a root folder

    The filename will be based on the "workfile" template defined in the
    project["config"]["template"].

    """

    def __init__(self, parent, root):
        super(NameWindow, self).__init__(parent=parent)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

        self.result = None
        self.host = api.registered_host()
        self.root = self.host.work_root()
        self.work_file = None

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

        # Define work files template
        templates = self.data["project"]["config"]["template"]
        template = templates.get("workfile",
                                 "{task[name]}_v{version:0>4}<_{comment}>")
        self.template = template

        self.widgets = {
            "preview": QtWidgets.QLabel("Preview filename"),
            "comment": QtWidgets.QLineEdit(),
            "version": QtWidgets.QWidget(),
            "versionValue": QtWidgets.QSpinBox(),
            "versionCheck": QtWidgets.QCheckBox("Next Available Version"),
            "inputs": QtWidgets.QWidget(),
            "buttons": QtWidgets.QWidget(),
            "okButton": QtWidgets.QPushButton("Ok"),
            "cancelButton": QtWidgets.QPushButton("Cancel")
        }

        # Build version
        self.widgets["versionValue"].setMinimum(1)
        self.widgets["versionValue"].setMaximum(9999)
        self.widgets["versionCheck"].setCheckState(QtCore.Qt.CheckState(2))
        layout = QtWidgets.QHBoxLayout(self.widgets["version"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widgets["versionValue"])
        layout.addWidget(self.widgets["versionCheck"])

        # Build buttons
        layout = QtWidgets.QHBoxLayout(self.widgets["buttons"])
        layout.addWidget(self.widgets["okButton"])
        layout.addWidget(self.widgets["cancelButton"])

        # Build inputs
        layout = QtWidgets.QFormLayout(self.widgets["inputs"])
        layout.addRow("Version:", self.widgets["version"])
        layout.addRow("Comment:", self.widgets["comment"])
        layout.addRow("Preview:", self.widgets["preview"])

        # Build layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.widgets["inputs"])
        layout.addWidget(self.widgets["buttons"])

        self.widgets["versionValue"].valueChanged.connect(
            self.on_version_spinbox_changed
        )
        self.widgets["versionCheck"].stateChanged.connect(
            self.on_version_checkbox_changed
        )
        self.widgets["comment"].textChanged.connect(self.on_comment_changed)
        self.widgets["okButton"].pressed.connect(self.on_ok_pressed)
        self.widgets["cancelButton"].pressed.connect(self.on_cancel_pressed)

        # Allow "Enter" key to accept the save.
        self.widgets["okButton"].setDefault(True)

        # Force default focus to comment, some hosts didn't automatically
        # apply focus to this line edit (e.g. Houdini)
        self.widgets["comment"].setFocus()

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

        # Since the version can be padded with "{version:0>4}" we only search
        # for "{version".
        if "{version" not in self.template:
            # todo: hide the full row
            self.widgets["version"].setVisible(False)

        # Build comment
        if "{comment}" not in self.template:
            # todo: hide the full row
            self.widgets["comment"].setVisible(False)

        if self.widgets["versionCheck"].isChecked():
            self.widgets["versionValue"].setEnabled(False)

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
            self.widgets["versionValue"].setEnabled(True)
            self.data["version"] = self.widgets["versionValue"].value()

        self.work_file = self.get_work_file()

        preview = self.widgets["preview"]
        ok = self.widgets["okButton"]
        preview.setText(
            "<font color='green'>{0}</font>".format(self.work_file)
        )
        if os.path.exists(os.path.join(self.root, self.work_file)):
            preview.setText(
                "<font color='red'>Cannot create \"{0}\" because file exists!"
                "</font>".format(self.work_file)
            )
            ok.setEnabled(False)
        else:
            ok.setEnabled(True)


class ContextBreadcrumb(QtWidgets.QWidget):
    """Horizontal widget showing current avalon project, asset and task."""

    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        self.context = {}
        self.widgets = {
            "projectIcon": QtWidgets.QLabel(),
            "assetIcon": QtWidgets.QLabel(),
            "project": QtWidgets.QLabel(),
            "asset": QtWidgets.QLabel(),
            "task": QtWidgets.QLabel(),
            "taskIcon": QtWidgets.QLabel(),
        }

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.widgets["projectIcon"])
        layout.addWidget(self.widgets["project"])
        layout.addWidget(QtWidgets.QLabel(u"\u25B6"))
        layout.addWidget(self.widgets["assetIcon"])
        layout.addWidget(self.widgets["asset"])
        layout.addWidget(QtWidgets.QLabel(u"\u25B6"))
        layout.addWidget(self.widgets["taskIcon"])
        layout.addWidget(self.widgets["task"])
        layout.addStretch()

        for name in ["project", "asset", "task"]:
            self.widgets[name].setStyleSheet("QLabel{ font-size: 12pt; }")

    def refresh(self):

        self.context = {
            "project": api.Session["AVALON_PROJECT"],
            "asset": api.Session["AVALON_ASSET"],
            "task": api.Session["AVALON_TASK"]
        }

        # Refresh labels
        for key, value in self.context.items():
            self.widgets[key].setText(value)

        # todo: match icons from database when supplied
        icons = {
            "projectIcon": "fa.map",
            "assetIcon": "fa.plus-square",
            "taskIcon": "fa.male"
        }

        for key, value in icons.items():
            icon = qtawesome.icon(value,
                                  color=style.colors.default).pixmap(18, 18)
            self.widgets[key].setPixmap(icon)


class TasksWidget(QtWidgets.QWidget):
    def __init__(self):
        super(TasksWidget, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)

        view = QtWidgets.QTreeView()
        view.setIndentation(0)
        model = TasksModel()
        view.setModel(model)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        # Hide the default tasks "count" as we don't need that data here.
        view.setColumnHidden(1, True)

        self.models = {
            "tasks": model
        }

        self.widgets = {
            "view": view,
        }

        self._last_selected_task = None

    def set_asset(self, asset_id):

        # Try and preserve the last selected task and reselect it
        # after switching assets. If there's no currently selected
        # asset keep whatever the "last selected" was prior to it.
        current = self.get_current_task()
        if current:
            self._last_selected_task = current

        self.models["tasks"].set_assets([asset_id])

        if self._last_selected_task:
            self.select_task(self._last_selected_task)

    def select_task(self, task):
        """Select a task by name.

        If the task does not exist in the current model then selection is only
        cleared.

        Args:
            task (str): Name of the task to select.

        """

        # Clear selection
        view = self.widgets["view"]
        model = view.model()
        selection_model = view.selectionModel()
        selection_model.clearSelection()

        # Select the task
        mode = selection_model.Select | selection_model.Rows
        for row in range(model.rowCount(QtCore.QModelIndex())):
            index = model.index(row, 0, QtCore.QModelIndex())
            name = index.data(QtCore.Qt.DisplayRole)
            if name == task:
                selection_model.select(index, mode)

                # Set the currently active index
                view.setCurrentIndex(index)

    def get_current_task(self):
        """Return name of task at current index (selected)

        Returns:
            str: Name of the current task.

        """
        view = self.widgets["view"]
        index = view.currentIndex()
        index = index.sibling(index.row(), 0)  # ensure column zero for name
        return index.data(QtCore.Qt.DisplayRole)


class FilesWidget(QtWidgets.QWidget):
    """A widget displaying files that allows to save"""
    # todo: separate out the files display from window
    pass


class Window(QtWidgets.QMainWindow):
    """Work Files Window"""
    title = "Work Files"

    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle(self.title)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        # Setup
        self.root = None
        self.host = api.registered_host()

        pages = {
            "home": QtWidgets.QWidget()
        }

        widgets = {
            "pages": QtWidgets.QStackedWidget(),
            "header": ContextBreadcrumb(),
            "body": QtWidgets.QWidget(),
            "assets": AssetWidget(silo_creatable=False),
            "tasks": TasksWidget(),
            "files": QtWidgets.QWidget(),
            "fileList": QtWidgets.QListWidget(),
            "fileDuplicate": QtWidgets.QPushButton("Duplicate"),
            "fileOpen": QtWidgets.QPushButton("Open"),
            "fileBrowse": QtWidgets.QPushButton("Browse"),
            "fileCurrent": QtWidgets.QLabel(),
            "fileSave": QtWidgets.QPushButton("Save As")
        }

        self.setCentralWidget(widgets["pages"])
        widgets["pages"].addWidget(pages["home"])

        # Build homepage
        layout = QtWidgets.QVBoxLayout(pages["home"])
        layout.addWidget(widgets["header"])
        layout.addWidget(widgets["body"])

        # Build body
        layout = QtWidgets.QHBoxLayout(widgets["body"])
        layout.addWidget(widgets["assets"])
        layout.addWidget(widgets["tasks"])
        layout.addWidget(widgets["files"])

        # Build buttons widget for files widget
        buttons = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["fileDuplicate"])
        layout.addWidget(widgets["fileOpen"])
        layout.addWidget(widgets["fileBrowse"])

        # Build files widgets
        layout = QtWidgets.QVBoxLayout(widgets["files"])
        layout.addWidget(widgets["fileList"])
        layout.addWidget(buttons)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Plain)
        layout.addWidget(separator)

        layout.addWidget(widgets["fileCurrent"])
        layout.addWidget(widgets["fileSave"])

        widgets["fileDuplicate"].pressed.connect(self.on_duplicate_pressed)
        widgets["fileOpen"].pressed.connect(self.on_open_pressed)
        widgets["fileList"].doubleClicked.connect(self.on_open_pressed)
        widgets["tasks"].widgets["view"].doubleClicked.connect(
            self.on_task_pressed
        )
        widgets["fileBrowse"].pressed.connect(self.on_browse_pressed)
        widgets["fileSave"].pressed.connect(self.on_save_as_pressed)

        # Force focus on the open button by default, required for Houdini.
        widgets["fileOpen"].setFocus()

        # Connect signals
        widgets["assets"].current_changed.connect(self.on_asset_changed)

        self.widgets = widgets

        self.refresh()
        self.resize(750, 500)

    def set_context(self, context):

        if "asset" in context:
            asset = context["asset"]
            asset_document = io.find_one({"name": asset,
                                          "type": "asset"})

            # Set silo
            silo = asset_document["data"].get("silo")
            if self.widgets["assets"].get_current_silo() != silo:
                self.widgets["assets"].set_silo(silo)

            # Select the asset
            self.widgets["assets"].select_assets([asset], expand=True)

        if "task" in context:
            self.widgets["tasks"].select_task(context["task"])

    def get_filename(self):
        """Show save dialog to define filename for save or duplicate

        Returns:
            str: The filename to create.

        """
        window = NameWindow(parent=self,
                            root=self.root)
        window.exec_()

        return window.get_result()

    def refresh(self):

        self.root = self.host.work_root()

        # Refresh asset widget
        self.widgets["assets"].refresh()

        # Refresh current scene label
        filepath = self.host.current_file()
        current = os.path.basename(filepath) if filepath else "<unsaved>"
        self.widgets["fileCurrent"].setText("Current File: %s" % current)

        # Refresh breadcrumbs
        self.widgets["header"].refresh()

        # Refresh files list
        file_list = self.widgets["fileList"]
        file_list.clear()

        modified = []
        extensions = set(self.host.file_extensions())

        if os.path.exists(self.root):
            for f in sorted(os.listdir(self.root)):
                path = os.path.join(self.root, f)
                if os.path.isdir(path):
                    continue

                if extensions and os.path.splitext(f)[1] not in extensions:
                    continue

                file_list.addItem(f)
                modified.append(os.path.getmtime(path))
        else:
            log.warning("Work root does not exist: %s" % self.root)

        # Select last modified file
        if file_list.count():
            item = file_list.item(modified.index(max(modified)))
            item.setSelected(True)

            # Scroll list so item is visible
            def callback():
                """Delayed callback to scroll to the item"""
                self.widgets["fileList"].scrollToItem(item)

            QtCore.QTimer.singleShot(100, callback)

            self.widgets["fileDuplicate"].setEnabled(True)
        else:
            self.widgets["fileDuplicate"].setEnabled(False)

        file_list.setMinimumWidth(file_list.sizeHintForColumn(0) + 30)

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
                host.save(host.current_file())

            else:
                # Don't save, continue to open file
                pass

        return host.open(filepath)

    def on_duplicate_pressed(self):
        work_file = self.get_filename()

        if not work_file:
            return

        src = os.path.join(
            self.root, self.widgets["fileList"].selectedItems()[0].text()
        )
        dst = os.path.join(
            self.root, work_file
        )
        shutil.copy(src, dst)

        self.refresh()

    def on_open_pressed(self):

        selection = self.widgets["fileList"].selectedItems()
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
        work_file = self.get_filename()

        if not work_file:
            return

        file_path = os.path.join(self.root, work_file)
        self.host.save(file_path)

        self.close()

    def on_asset_changed(self):
        asset = self.widgets["assets"].get_active_asset()
        self.widgets["tasks"].set_asset(asset)

    def on_task_pressed(self):

        asset_id = self.widgets["assets"].get_active_asset()
        if not asset_id:
            log.warning("No asset selected.")
            return

        task_name = self.widgets["tasks"].get_current_task()
        if not task_name:
            log.warning("No task selected.")
            return

        # Get the asset name from asset id.
        asset = io.find_one({"_id": io.ObjectId(asset_id), "type": "asset"})
        if not asset:
            log.error("Invalid asset id: %s" % asset_id)
            return

        asset_name = asset["name"]
        api.update_current_task(task=task_name, asset=asset_name)

        self.refresh()


def show(root=None, debug=False):
    """Show Work Files GUI"""
    # todo: remove `root` argument to show()

    host = api.registered_host()
    if host is None:
        raise RuntimeError("No registered host.")

    # Verify the host has implemented the api for Work Files
    required = ["open",
                "save",
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

    if debug:
        api.Session["AVALON_ASSET"] = "Mock"
        api.Session["AVALON_TASK"] = "Testing"

    with tools_lib.application():
        global window
        window = Window()
        window.setStyleSheet(style.load_stylesheet())

        if debug:
            # Enable closing in standalone
            window.show()
            return window

        else:
            # Cause modal dialog
            # todo: force modal again
            window.show()
            return window
