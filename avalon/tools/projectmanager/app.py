import sys

from functools import partial
from copy import deepcopy

from ...vendor.Qt import QtWidgets, QtCore, QtGui
from ...vendor import qargparse, qtawesome
from ... import io, schema, api, style

from .. import lib as tools_lib
from ..widgets import AssetWidget
from ..models import TasksModel

from .dialogs import TasksCreateDialog, AssetCreateDialog

module = sys.modules[__name__]
module.window = None


class GroupBoxMessage(QtWidgets.QGroupBox):

    def __init__(self, title, parent=None):
        super(GroupBoxMessage, self).__init__(title, parent)

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

        self.message = status_label

    def set_message(self, message):
        self.message.setText(message)


class TaskOptionContainer(QtWidgets.QScrollArea):

    def __init__(self, parent=None):
        super(TaskOptionContainer, self).__init__(parent)

        self.task = None
        self.parsers = None
        self.is_batch = False

    def empty(self, message):
        status = GroupBoxMessage("")
        status.set_message(message)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.addWidget(status)

        # Reset
        self.task = None
        self.parsers = None
        self.is_batch = False

        self.setWidget(widget)
        self.setWidgetResizable(True)

    def add_options(self, parsers, task, is_batch):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        for parser in parsers:
            layout.addWidget(parser)

        self.task = task
        self.parsers = parsers
        self.is_batch = is_batch

        self.setWidget(widget)
        self.setWidgetResizable(False)

    def save_options(self, assets):
        if self.task is None or self.parsers is None:
            return  # Possibly a bug.

        changes = dict()
        task_name = self.task["name"]
        option_names = self.task["options"].keys()
        filed_template = "data.task_options.{task}.{option}"

        for parser in self.parsers:
            asset_name = parser._desciption
            if asset_name not in changes:
                changes[asset_name] = dict()
            for option_name in option_names:
                arg = parser.find(option_name)
                value = arg.read()
                field = filed_template.format(task=task_name,
                                              option=option_name)
                changes[asset_name].update({field: {"value": value}})
                # Update cache
                # (TODO) This doesn't work
                print(assets[asset_name]["data"])
                doc = assets[asset_name]["data"]
                nested_keys = ["task_options", task_name, option_name]
                for key in nested_keys:
                    if key not in doc:
                        doc[key] = dict()
                    doc = doc[key]
                doc["value"] = value
                print(assets[asset_name]["data"])

        if self.is_batch:
            filter_ = {"_id": {"$in": [_["_id"] for _ in assets.values()]}}
            io.update_many(filter_, {"$set": changes.popitem()[1]})

        else:
            for asset_name, options in changes.items():
                filter_ = {"_id": assets[asset_name]["_id"]}
                io.update_many(filter_, {"$set": options})


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
        task_view = QtWidgets.QTreeView()
        task_view.setIndentation(0)
        task_model = TasksModel()
        task_view.setModel(task_model)
        add_task = QtWidgets.QPushButton("Add task")
        tasks_layout.addWidget(label)
        tasks_layout.addWidget(task_view)
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
        body.setStretchFactor(2, 65)

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
                "tasks": task_model,
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
        options_batch.stateChanged.connect(self.on_batch_changed)
        assets.selection_changed.connect(self.on_asset_changed)
        task_view.selectionModel().selectionChanged.connect(self.on_task_changed)

        self.task_options_refresh()  # Init
        self.resize(800, 500)

        self.echo("Connected to project: {0}".format(project_name))

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
        self.task_options_refresh()

    def on_task_changed(self, selected, deselected):
        """
        Callback on task selection changed.

        This updates the task extra option view.
        """
        indexes = []
        for index in selected.indexes():
            if index.column() == 0:
                indexes.append(index)

        if not indexes:
            self.task_options_refresh()
            return

        # Only one task will be selected
        tasks_model = self.data["model"]["tasks"]
        task_name = tasks_model.data(indexes[0], 0)
        self.task_options_refresh(task_name)

    def on_batch_changed(self, state):
        task = None
        container = self.data["options"]["container"]
        if container.task is not None:
            task = container.task["name"]
        self.task_options_refresh(task)

    def on_task_options_accepted(self):
        container = self.data["options"]["container"]
        model = self.data["model"]["assets"]

        assets = dict()
        for asset in model.get_selected_assets():
            assets[asset["name"]] = asset
        container.save_options(assets)

    def task_options_refresh(self, selected_task=None):
        accept = self.data["options"]["accept"]
        container = self.data["options"]["container"]

        if selected_task is None:
            message = "Select task to view options."
            container.empty(message)
            accept.setEnabled(False)
            return

        # Create options
        project = self.data["project"]
        model = self.data["model"]["assets"]
        batch_edit = self.data["options"]["batch"]
        task_options = None

        for task in project["config"]["tasks"]:
            if task["name"] == selected_task and "options" in task:
                task_options = deepcopy(task)
                break
        else:
            message = "No task options."
            container.empty(message)
            accept.setEnabled(False)
            return

        parsers = list()
        is_batch = batch_edit.checkState()

        def add_options(_parser, data=None):
            for name, opt in task_options["options"].items():
                kwargs = {k: opt[k] for k in ["label", "help"]
                          if k in opt}
                arg = _parser.add_argument(name,
                                           default=opt.get("default_value"),
                                           **kwargs)
                if data:
                    nested_keys = ["task_options", selected_task, name]
                    for key in nested_keys:
                        data = data.get(key, {})
                    value = data.get("value")
                    if value is not None:
                        # Asset has task option setup
                        arg.write(value)

            parsers.append(_parser)

        if is_batch:
            # Batch edit mode will not present asset's task setup
            _label = "Batch set selected assets"
            parser = qargparse.QArgumentParser(description=_label)
            add_options(parser)

        else:
            for asset in model.get_selected_assets():
                asset_name = asset["name"]
                asset_data = asset["data"]
                parser = qargparse.QArgumentParser(description=asset_name)
                add_options(parser, asset_data)

        container.add_options(parsers, task=task_options, is_batch=is_batch)
        accept.setEnabled(True)


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
