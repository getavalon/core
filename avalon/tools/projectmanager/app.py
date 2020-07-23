import sys

from ...vendor.Qt import QtWidgets, QtCore, QtGui
from ...vendor import qargparse, qtawesome
from ... import io, schema, api, style

from .. import lib as tools_lib
from ..widgets import AssetWidget, TaskWidget

from .dialogs import TasksCreateDialog, AssetCreateDialog

module = sys.modules[__name__]
module.window = None


class MessageBox(QtWidgets.QWidget):
    """A widget that shows word wrapped message with exclamation icon

    Methods:
        set_message(str): Set a text message to display

    """

    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent)

        status_label = QtWidgets.QLabel("")
        status_label.setWordWrap(True)
        status_icon = QtWidgets.QLabel()
        status_icon.setPixmap(
            qtawesome.icon("fa.exclamation-circle",
                           color="#c6c6c6").pixmap(18, 18)
        )
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(status_icon)
        layout.addWidget(status_label, stretch=True)

        self._message = status_label

    def set_message(self, message):
        self._message.setText(message)


class TaskOptionContainer(QtWidgets.QScrollArea):
    """Scrollable task option widgets' container

    This widget hold a set of `qargparser.QArgumentParser` widget that
    aim to read/write task options' config per asset from/to database.

    """
    fetch_all = QtCore.Signal()
    BATCH = ":.batch.:"

    def __init__(self, parent=None):
        super(TaskOptionContainer, self).__init__(parent)
        self._has_active_read = False
        self.changes = None
        self.is_batch = False
        self.setAlignment(QtCore.Qt.AlignTop)

    def add_active_read(self, arg):
        """Read QArgument object's value without waiting it's signal
        """
        self.fetch_all.connect(arg.changed.emit)
        self._has_active_read = True

    def clear_active_read(self):
        # Avoid calling deleted objects
        if self._has_active_read:
            self.fetch_all.disconnect()
            self._has_active_read = False

    def empty(self, message):
        status = MessageBox()
        status.set_message(message)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.addWidget(status)
        # Reset
        self.changes = None
        self.is_batch = False

        self.setWidget(widget)
        self.setWidgetResizable(True)

    def add_options(self, parsers, is_batch):
        """Docking QArgumentParser widgets"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        for parser in parsers:
            layout.addWidget(parser)

        self.changes = None
        self.is_batch = is_batch

        self.setWidget(widget)
        self.setWidgetResizable(False)

    def update_change(self, value, option, asset, task):
        """Update option changes from QArgument object"""
        if self.changes is None:
            self.changes = dict()
        if asset not in self.changes:
            self.changes[asset] = dict()
        if task not in self.changes[asset]:
            self.changes[asset][task] = dict()

        self.changes[asset][task].update({option: value})

    def save_options(self, asset_ids):
        """Write per asset's task option configurations into database"""
        if self.is_batch:
            self.fetch_all.emit()

        if self.changes is None:
            return False

        field_template = "data.taskOptions.{task}.{option}.value"

        def compose(changes):
            operation = dict()
            for task, options in changes.items():
                for option, value in options.items():
                    field = field_template.format(task=task, option=option)
                    operation[field] = value
            return operation

        if self.is_batch:
            batch = compose(self.changes[self.BATCH])
            filter_ = {"_id": {"$in": list(asset_ids.values())}}
            io.update_many(filter_, {"$set": batch})
        else:
            for asset_name, tasks_options in self.changes.items():
                edits = compose(tasks_options)
                filter_ = {"_id": asset_ids[asset_name]}
                io.update_many(filter_, {"$set": edits})

        return True


class Window(QtWidgets.QDialog):
    """Project manager interface

    """

    def __init__(self, is_silo_project=None, parent=None):
        super(Window, self).__init__(parent)
        project_doc = io.find_one({"type": "project"})
        project_name = project_doc["name"]

        self.setWindowTitle("Project Manager ({0})".format(project_name))
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        if is_silo_project is None:
            is_silo_project = tools_lib.project_use_silo(project_doc)
        self.is_silo_project = is_silo_project

        # assets
        assets_widgets = QtWidgets.QWidget()
        assets_widgets.setContentsMargins(0, 0, 0, 0)
        assets_layout = QtWidgets.QVBoxLayout(assets_widgets)
        assets = AssetWidget()
        assets.view.setSelectionMode(assets.view.ExtendedSelection)
        add_asset = QtWidgets.QPushButton("Add asset")
        assets_layout.addWidget(assets)
        assets_layout.addWidget(add_asset)

        # tasks
        tasks_widgets = QtWidgets.QWidget()
        tasks_widgets.setContentsMargins(0, 0, 0, 0)
        tasks_layout = QtWidgets.QVBoxLayout(tasks_widgets)

        label = QtWidgets.QLabel("Tasks")
        label.setFixedHeight(28)
        tasks = TaskWidget()
        tasks.view.setSelectionMode(tasks.view.ExtendedSelection)
        add_task = QtWidgets.QPushButton("Add task")
        tasks_layout.addWidget(label)
        tasks_layout.addWidget(tasks)
        tasks_layout.addWidget(add_task)

        # task option widget
        options_widgets = QtWidgets.QWidget()
        options_widgets.setContentsMargins(0, 0, 0, 0)

        options_label = QtWidgets.QLabel("Tasks Options")
        options_batch = QtWidgets.QCheckBox("Batch Edit")
        options_container = TaskOptionContainer()
        options_accept = QtWidgets.QPushButton("Save")
        options_accept.setEnabled(False)

        options_layout = QtWidgets.QVBoxLayout(options_widgets)
        options_layout.addWidget(options_label)
        options_layout.addWidget(options_batch)
        options_layout.addWidget(options_container, stretch=True)
        options_layout.addWidget(options_accept)

        # set body layout
        body = QtWidgets.QSplitter()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        body.setOrientation(QtCore.Qt.Horizontal)
        body.addWidget(assets_widgets)
        body.addWidget(tasks_widgets)
        body.addWidget(options_widgets)
        body.setStretchFactor(0, 50)
        body.setStretchFactor(1, 65)
        body.setSizes([50, 65, 0])  # Hide task options by default

        # statusbar
        message = QtWidgets.QLabel()
        message.setFixedHeight(20)

        statusbar = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(statusbar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(message)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(statusbar)

        self.data = {
            "label": {
                "message": message,
            },
            "model": {
                "assets": assets,
                "tasks": tasks,
            },
            "buttons": {
                "add_asset": add_asset,
                "add_task": add_task
            },
            "options": {
                "accept": options_accept,
                "batch": options_batch,
                "container": options_container,
            },
            "project": project_doc,
        }

        # signals
        add_asset.clicked.connect(self.on_add_asset)
        add_task.clicked.connect(self.on_add_task)
        options_accept.clicked.connect(self.on_task_options_accepted)
        options_batch.stateChanged.connect(self.on_task_changed)
        tasks.selection_changed.connect(self.on_task_changed)
        assets.selection_changed.connect(self.on_asset_changed)

        self.resize(900, 500)

        self.echo("Connected to project: {0}".format(project_name))

        # (TODO) Shouldn't need to call this, but since `AssetModel`
        #   already made changes on it's init..
        self.on_task_changed()

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands
        whilst trying to name an instance.

        """

    def refresh(self):
        self.data["project"] = io.find_one({"type": "project"})
        self.data["model"]["assets"].refresh()

    def echo(self, message):
        widget = self.data["label"]["message"]
        widget.setText(str(message))

        QtCore.QTimer.singleShot(5000, lambda: widget.setText(""))

        print(message)

    def on_add_asset(self):
        """Show add asset dialog"""

        # Get parent asset (active index in selection)
        model = self.data["model"]["assets"]
        parent = model.get_active_asset()

        if parent and parent["type"] == "silo":
            parent_id = None
            silo = parent["name"]
        else:
            parent_id = parent["_id"] if parent else None
            silo = parent.get("_document", {}).get("silo") if parent else None

        dialog = AssetCreateDialog(
            is_silo_required=self.is_silo_project, parent=self
        )
        if self.is_silo_project:
            dialog.set_silo_input_enable(
                parent_id is None or silo is None
            )

        def _on_asset_created(data):
            """Callback whenever asset gets created"""
            self.echo("Added asset: {label} ({name})".format(**data))
            model.refresh()

            # Preserve focus on the dialog label field
            # This is to allow quick continuing of typing a new asset name
            # whenever the user created one; this way we can press the "ENTER"
            # key to add an asset and continue typing for the next.
            dialog.data["label"]["label"].setFocus()

        def _on_current_asset_changed():
            """Callback on current asset changed in item widget.

            Whenever the current index changes in the item widget we want to
            update under which asset we're creating *to be created* asset.

            """

            parent = model.get_active_asset()
            if parent and parent["type"] == "silo":
                _parent_id = None
                _silo = parent["name"]
            else:
                _parent_id = parent["_id"] if parent else None
                _silo = None
                if parent:
                    _silo = parent.get("_document", {}).get("silo")

            dialog.set_parent(_parent_id)
            dialog.set_silo(_silo)
            if self.is_silo_project:
                dialog.set_silo_input_enable(
                    _parent_id is None or _silo is None
                )

        # Set initial values
        dialog.set_parent(parent_id)
        dialog.set_silo(silo)

        # Signals
        model.current_changed.connect(_on_current_asset_changed)
        dialog.asset_created.connect(_on_asset_created)

        dialog.show()

    def on_add_task(self):
        """Add a task by user input"""

        # Ask the user what tasks to create
        dialog = TasksCreateDialog(parent=self)
        dialog.exec_()

        if not dialog.result():
            return

        tasks = dialog.get_selected()
        if not tasks:
            return

        # Add tasks in database for selected assets
        model = self.data["model"]["assets"]
        selected = model.get_selected_assets()
        for asset in selected:
            _filter = {"_id": asset["_id"]}
            asset_tasks = asset.get("data", {}).get("tasks", [])
            for task in tasks:
                if task not in asset_tasks:
                    asset_tasks.append(task)

            # Update the field
            asset["data"]["tasks"] = asset_tasks

            schema.validate(asset)
            io.replace_one(_filter, asset)

        # Refresh assets from db and the tasks model with new task
        self.refresh()
        self.on_asset_changed()

        self.echo("Added tasks: {0}".format(", ".join(tasks)))

    def on_asset_changed(self):
        """Callback on asset selection changed

        This updates the task view.

        """

        model = self.data["model"]["assets"]
        selected = model.get_selected_assets()
        self.data["model"]["tasks"].set_assets(selected)
        self.on_task_changed()

    def on_task_changed(self):
        """Callback on task selection changed

        This updates the task extra option view.

        """
        accept = self.data["options"]["accept"]
        container = self.data["options"]["container"]
        tasks = self.data["model"]["tasks"]

        task_names = tasks.get_selected_tasks()

        if not task_names:
            message = "Select tasks to view options."
            container.empty(message)
            accept.setEnabled(False)
            return

        # Create options
        project = self.data["project"]
        model = self.data["model"]["assets"]
        options_batch = self.data["options"]["batch"]
        task_options = dict()

        for task in project["config"]["tasks"]:
            if task["name"] in task_names and "options" in task:
                task_options[task["name"]] = task

        if not task_options:
            message = "No task options."
            container.empty(message)
            accept.setEnabled(False)
            return

        parsers = list()
        is_batch = options_batch.checkState()
        container.clear_active_read()

        def walk(data, fields):
            for key in fields:
                data = data.get(key, {})
            return data

        def setup(_parser, data=None, _asset=None):
            for _task in task_names:
                if _task not in task_options:
                    continue  # `_task` has no option registered in project

                for name, opt in task_options[_task]["options"].items():
                    d = walk(data or {}, fields=["taskOptions", _task, name])
                    value = d.get("value")
                    arg = _parser.add_argument(
                        name,
                        _asset=_asset,  # additional info
                        _task=_task,  # additional info
                        **opt
                    )
                    if value is not None:
                        # Asset has task option setup
                        arg.write(value)

                    if is_batch:
                        # When batch mode enabled, no matter user has changed
                        # the value or not, all setup should be written into
                        # database.
                        container.add_active_read(arg)

            _parser.changed.connect(self.on_task_options_changed)
            parsers.append(_parser)

        if is_batch:
            # Batch edit mode will not present asset's task setup
            _label = "Batch set selected assets"
            parser = qargparse.QArgumentParser(description=_label)
            setup(parser, _asset=container.BATCH)

        else:
            for asset in model.get_selected_assets():
                asset_name = asset["name"]
                asset_data = asset["data"]
                parser = qargparse.QArgumentParser(description=asset_name)
                setup(parser, asset_data, _asset=asset_name)

        container.add_options(parsers, is_batch=is_batch)
        accept.setEnabled(True)

    def on_task_options_accepted(self):
        container = self.data["options"]["container"]
        options_batch = self.data["options"]["batch"]
        model = self.data["model"]["assets"]

        selected_asset_ids = dict()
        for asset in model.get_selected_assets():
            selected_asset_ids[asset["name"]] = asset["_id"]

        # Write database if any changed
        changed = container.save_options(selected_asset_ids)
        # Update asset model data if changed
        if changed:
            model.update_selected_assets()
        # Disable batch edit to view update
        if container.is_batch:
            options_batch.setCheckState(QtCore.Qt.Unchecked)

    def on_task_options_changed(self, arg):
        container = self.data["options"]["container"]
        container.update_change(value=arg.read(),
                                option=arg["name"],
                                asset=arg["_asset"],
                                task=arg["_task"])


def show(root=None, debug=False, parent=None):
    """Display Loader GUI

    Arguments:
        debug (bool, optional): Run loader in debug-mode,
            defaults to False
        parent (QtCore.QObject, optional): When provided parent the interface
            to this QObject.

    """

    try:
        module.window.close()
        del module.window
    except (RuntimeError, AttributeError):
        pass

    if debug is True:
        io.install()

    with tools_lib.application():
        window = Window(parent=parent)
        window.show()
        window.setStyleSheet(style.load_stylesheet())
        window.refresh()

        module.window = window

        # Pull window to the front.
        module.window.raise_()
        module.window.activateWindow()


def cli(args):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("project")

    args = parser.parse_args(args)
    project = args.project

    io.install()

    api.Session["AVALON_PROJECT"] = project

    show()
