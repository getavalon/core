import sys
import os
import getpass
import re
import shutil
import logging
import platform

from ...vendor.Qt import QtWidgets, QtCore
from ...vendor import qtawesome
from ... import style, io, api, pipeline

from .. import lib as tools_lib
from ..widgets import AssetWidget
from ..models import TasksModel

log = logging.getLogger(__name__)

module = sys.modules[__name__]
module.window = None


class NameWindow(QtWidgets.QDialog):
    """Name Window to define a unique filename inside a root folder

    The filename will be based on the "workfile" template defined in the
    project["config"]["template"].

    """

    def __init__(self, parent, root, session=None):
        super(NameWindow, self).__init__(parent=parent)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

        self.result = None
        self.host = api.registered_host()
        self.root = root
        self.work_file = None

        if session is None:
            # Fallback to active session
            session = api.Session

        # Set work file data for template formatting
        self.data = {
            "project": io.find_one(
                {"name": session["AVALON_PROJECT"], "type": "project"}
            ),
            "asset": io.find_one(
                {"name": session["AVALON_ASSET"], "type": "asset"}
            ),
            "task": {
                "name": session["AVALON_TASK"].lower(),
                "label": session["AVALON_TASK"]
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

            # Match with ignore case on Windows due to the Windows
            # OS not being case-sensitive. This avoids later running
            # into the error that the file did exist if it existed
            # with a different upper/lower-case.
            kwargs = {}
            if platform.system() == "Windows":
                kwargs["flags"] = re.IGNORECASE

            # Get highest version among existing matching files
            version = 1
            for file in sorted(files):
                match = re.match(template, file, **kwargs)
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
        self.set_session(api.Session)

    def set_session(self, session):

        self.context = {
            "project": session["AVALON_PROJECT"],
            "asset": session["AVALON_ASSET"],
            "task": session["AVALON_TASK"]
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

    task_changed = QtCore.Signal()

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

        selection = view.selectionModel()
        #selection.selectionChanged.connect(self.selection_changed)
        selection.currentChanged.connect(self.task_changed)

        self.models = {
            "tasks": model
        }

        self.widgets = {
            "view": view,
        }

        self._last_selected_task = None

    def set_asset(self, asset_id):

        if asset_id is None:
            # Asset deselected
            return

        # Try and preserve the last selected task and reselect it
        # after switching assets. If there's no currently selected
        # asset keep whatever the "last selected" was prior to it.
        current = self.get_current_task()
        if current:
            self._last_selected_task = current

        self.models["tasks"].set_assets([asset_id])

        if self._last_selected_task:
            self.select_task(self._last_selected_task)

        # Force a task changed emit.
        self.task_changed.emit()

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
    def __init__(self, parent=None):
        super(FilesWidget, self).__init__(parent=parent)

        # Setup
        self._asset = None
        self._task = None
        self.root = None
        self.host = api.registered_host()

        widgets = {
            "list": QtWidgets.QListWidget(),
            "duplicate": QtWidgets.QPushButton("Duplicate"),
            "open": QtWidgets.QPushButton("Open"),
            "browse": QtWidgets.QPushButton("Browse"),
            #"currentFile": QtWidgets.QLabel(),
            "save": QtWidgets.QPushButton("Save As")
        }

        # Build buttons widget for files widget
        buttons = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.addWidget(widgets["duplicate"])
        layout.addWidget(widgets["open"])
        layout.addWidget(widgets["browse"])

        # Build files widgets
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["list"])
        layout.addWidget(buttons)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Plain)
        layout.addWidget(separator)

        #layout.addWidget(widgets["currentFile"])
        layout.addWidget(widgets["save"])

        widgets["list"].doubleClicked.connect(self.on_open_pressed)
        widgets["duplicate"].pressed.connect(self.on_duplicate_pressed)
        widgets["open"].pressed.connect(self.on_open_pressed)
        widgets["browse"].pressed.connect(self.on_browse_pressed)
        widgets["save"].pressed.connect(self.on_save_as_pressed)

        self.widgets = widgets

    def set_asset_task(self, asset, task):
        self._asset = asset
        self._task = task

    def _get_session(self):
        """Return a modified session for the current asset and task"""

        session = api.Session.copy()
        # todo: expose this in the API?
        changes = pipeline.compute_session_changes(session,
                                                   asset=self._asset,
                                                   task=self._task)
        session.update(changes)

        return session

    def _enter_session(self):
        """Enter the asset and task session currently selected"""

        session = api.Session.copy()
        changes = pipeline.compute_session_changes(session,
                                                   asset=self._asset,
                                                   task=self._task)
        if not changes:
            # Return early if we're already in the right Session context
            # to avoid any unwanted Task Changed callbacks to be triggered.
            return

        api.update_current_task(asset=self._asset, task=self._task)

    def open_file(self, filepath):
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

        self._enter_session()
        return host.open_file(filepath)

    def save_changes_prompt(self):
        messagebox = QtWidgets.QMessageBox(parent=self)
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

    def get_filename(self):
        """Show save dialog to define filename for save or duplicate

        Returns:
            str: The filename to create.

        """
        session = self._get_session()

        window = NameWindow(parent=self,
                            root=self.root,
                            session=session)
        window.exec_()

        return window.get_result()

    def on_duplicate_pressed(self):
        work_file = self.get_filename()

        if not work_file:
            return

        src = os.path.join(
            self.root, self.widgets["list"].selectedItems()[0].text()
        )
        dst = os.path.join(
            self.root, work_file
        )
        shutil.copy(src, dst)

        self.refresh()

    def on_open_pressed(self):

        selection = self.widgets["list"].selectedItems()
        if not selection:
            print("No file selected to open..")
            return

        work_file = os.path.join(self.root, selection[0].text())
        return self.open_file(work_file)

    def on_browse_pressed(self):

        filter = " *".join(self.host.file_extensions())
        filter = "Work File (*{0})".format(filter)
        work_file = QtWidgets.QFileDialog.getOpenFileName(
            caption="Work Files",
            dir=self.root,
            filter=filter
        )[0]

        if not work_file:
            return

        self.open_file(work_file)

    def on_save_as_pressed(self):
        work_file = self.get_filename()

        if not work_file:
            return

        file_path = os.path.join(self.root, work_file)

        self._enter_session()   # Make sure we are in the right session
        self.host.save_file(file_path)
        self.refresh()

    def refresh(self):
        """Refresh listed files for current selection in the interface"""

        # Refresh current scene label
        #filepath = self.host.current_file()
        #current = os.path.basename(filepath) if filepath else "<unsaved>"
        #self.widgets["currentFile"].setText("Current File: %s" % current)

        # Clear the list
        file_list = self.widgets["list"]
        file_list.clear()

        if not self._asset:
            # No asset selected
            return

        if not self._task:
            # No task selected
            return

        # Define a custom session so we can query the work root
        # for a "Work area" that is not our current Session.
        # This way we can browse it even before we enter it.
        # todo: refactor to use pipeline.compute_session_changes()
        session = get_asset_task_session(self._asset, self._task)
        self.root = self.host.work_root(session)

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
                self.widgets["list"].scrollToItem(item)

            QtCore.QTimer.singleShot(100, callback)

            self.widgets["duplicate"].setEnabled(True)
        else:
            self.widgets["duplicate"].setEnabled(False)

        file_list.setMinimumWidth(file_list.sizeHintForColumn(0) + 30)


class Window(QtWidgets.QMainWindow):
    """Work Files Window"""
    title = "Work Files"

    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.setWindowTitle(self.title)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)

        pages = {
            "home": QtWidgets.QWidget()
        }

        widgets = {
            "pages": QtWidgets.QStackedWidget(),
            "header": ContextBreadcrumb(),
            "body": QtWidgets.QWidget(),
            "assets": AssetWidget(silo_creatable=False),
            "tasks": TasksWidget(),
            "files": FilesWidget()
        }

        self.setCentralWidget(widgets["pages"])
        widgets["pages"].addWidget(pages["home"])

        # Build home
        layout = QtWidgets.QVBoxLayout(pages["home"])
        #layout.addWidget(widgets["header"])
        layout.addWidget(widgets["body"])

        # Build home - body
        layout = QtWidgets.QVBoxLayout(widgets["body"])
        split = QtWidgets.QSplitter()
        split.addWidget(widgets["assets"])
        split.addWidget(widgets["tasks"])
        split.addWidget(widgets["files"])
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 1)
        split.setStretchFactor(2, 3)
        layout.addWidget(split)

        # Connect signals
        widgets["tasks"].widgets["view"].doubleClicked.connect(
            self.on_task_pressed
        )
        widgets["assets"].current_changed.connect(self.on_asset_changed)
        widgets["tasks"].task_changed.connect(self.on_task_changed)

        self.widgets = widgets
        self.refresh()

        # Force focus on the open button by default, required for Houdini.
        self.widgets["files"].widgets["open"].setFocus()

        self.resize(900, 600)

    def on_task_changed(self):
        # Since we query the disk give it slightly more delay
        tools_lib.schedule(self._on_task_changed, 100, channel="mongo")

    def on_asset_changed(self):
        tools_lib.schedule(self._on_asset_changed, 50, channel="mongo")

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

            # Force a refresh on Tasks?
            self.widgets["tasks"].set_asset(asset_id=asset_document["_id"])

        if "task" in context:
            self.widgets["tasks"].select_task(context["task"])

    def refresh(self):

        # Refresh asset widget
        self.widgets["assets"].refresh()

        # Refresh breadcrumbs
        #self.widgets["header"].set_session(session)

        self._on_task_changed()

    def _on_asset_changed(self):
        asset = self.widgets["assets"].get_active_asset()

        if not asset:
            # Force disable the other widgets if no
            # active selection
            self.widgets["tasks"].setEnabled(False)
            self.widgets["files"].setEnabled(False)
        else:
            self.widgets["tasks"].setEnabled(True)

        self.widgets["tasks"].set_asset(asset)

    def on_task_pressed(self):

        asset = self.widgets["assets"].get_active_asset_document()
        if not asset:
            log.warning("No asset selected.")
            return

        task_name = self.widgets["tasks"].get_current_task()
        if not task_name:
            log.warning("No task selected.")
            return

        asset_name = asset["name"]
        api.update_current_task(task=task_name, asset=asset_name)

        self.refresh()

    def _on_task_changed(self):

        asset = self.widgets["assets"].get_active_asset_document()
        task = self.widgets["tasks"].get_current_task()

        self.widgets["tasks"].setEnabled(bool(asset))
        self.widgets["files"].setEnabled(all([bool(task), bool(asset)]))

        files = self.widgets["files"]
        files.set_asset_task(asset, task)
        files.refresh()


def show(root=None, debug=False, parent=None, use_context=True):
    """Show Work Files GUI"""
    # todo: remove `root` argument to show()

    if module.window:
        module.window.close()
        del(module.window)

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

    if debug:
        api.Session["AVALON_ASSET"] = "Mock"
        api.Session["AVALON_TASK"] = "Testing"

    with tools_lib.application():

        window = Window(parent=parent)
        window.refresh()

        if use_context:
            context = {"asset": api.Session["AVALON_ASSET"],
                       "silo": api.Session["AVALON_SILO"],
                       "task": api.Session["AVALON_TASK"]}
            window.set_context(context)

        window.show()
        window.setStyleSheet(style.load_stylesheet())

        module.window = window
