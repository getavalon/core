import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import io, schema, api, style

from .. import lib as tools_lib
from ..widgets import AssetWidget
from ..models import TasksModel

from .dialogs import TasksCreateDialog, AssetCreateDialog

module = sys.modules[__name__]
module.window = None


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

        body = QtWidgets.QSplitter()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        body.setOrientation(QtCore.Qt.Horizontal)
        body.addWidget(assets_widgets)
        body.addWidget(tasks_widgets)
        body.setStretchFactor(0, 100)
        body.setStretchFactor(1, 65)

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
            }
        }

        # signals
        add_asset.clicked.connect(self.on_add_asset)
        add_task.clicked.connect(self.on_add_task)
        assets.selection_changed.connect(self.on_asset_changed)

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

        self.data["model"]["tasks"].set_assets(asset_docs=selected)


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
