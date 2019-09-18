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

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        project_name = io.active_project()
        self.setWindowTitle("Project Manager ({0})".format(project_name))
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

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
        assets.silo_changed.connect(self.on_silo_changed)

        self.resize(800, 500)

        self.echo("Connected to project: {0}".format(project_name))

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
        parent_id = model.get_active_asset()

        # Get active silo
        silo = model.get_current_silo()
        if not silo:
            QtWidgets.QMessageBox.critical(self, "Missing silo",
                                           "Please create a silo first.\n"
                                           "Use the + tab at the top left.")
            return

        dialog = AssetCreateDialog(parent=self)

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
            dialog.set_parent(parent)
            dialog.set_silo(model.get_current_silo())

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
        for asset_id in selected:
            _filter = {"_id": asset_id}
            asset = io.find_one(_filter)
            asset_tasks = asset.get("data", {}).get("tasks", [])
            for task in tasks:
                if task not in asset_tasks:
                    asset_tasks.append(task)

            # Update the field
            asset["data"]["tasks"] = asset_tasks

            schema.validate(asset)
            io.replace_one(_filter, asset)

        # Refresh the tasks model
        self.on_asset_changed()

        self.echo("Added tasks: {0}".format(", ".join(tasks)))

    def on_asset_changed(self):
        """Callback on asset selection changed

        This updates the task view.

        """

        model = self.data["model"]["assets"]
        selected = model.get_selected_assets()
        self.data["model"]["tasks"].set_assets(selected)

    def on_silo_changed(self, silo):
        """Callback on asset silo changed"""
        if silo:
            self.echo("Silo changed to: {0}".format(silo))


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
        window = Window(parent)
        window.setStyleSheet(style.load_stylesheet())
        window.show()
        window.refresh()

        module.window = window


def cli(args):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("project")

    args = parser.parse_args(args)
    project = args.project

    io.install()

    api.Session["AVALON_PROJECT"] = project

    show()
