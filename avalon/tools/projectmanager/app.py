import sys
import copy

from functools import partial

from ...vendor.Qt import QtWidgets, QtCore, QtGui
from ... import io, schema, api, style

from .. import lib as tools_lib
from ..widgets import AssetWidget
from ..models import TasksModel

from .dialogs import TasksCreateDialog, AssetCreateDialog

module = sys.modules[__name__]
module.window = None

import avalon.api
import avalon.io
from avalon.vendor import qargparse, qtawesome


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
        tasks_layout = QtWidgets.QGridLayout(tasks_widgets)

        label = QtWidgets.QLabel("Tasks")
        label.setFixedHeight(28)
        task_view = QtWidgets.QTreeView()
        task_view.setIndentation(0)
        task_model = TasksModel()
        task_view.setModel(task_model)
        add_task = QtWidgets.QPushButton("Add task")

        # task option widget
        self.tasks_option_view = QtWidgets.QWidget()
        self.tasks_option_view.setContentsMargins(0, 0, 0, 0)
        self.tasks_option_layout = QtWidgets.QVBoxLayout(self.tasks_option_view)
        self.tasks_option_layout.setAlignment(QtCore.Qt.AlignTop)

        option_top_label = QtWidgets.QLabel("Tasks Options")
        option_top_label.setFixedHeight(28)

        # "No option found" widget
        self.top_msg_group = QtWidgets.QGroupBox("", self)
        top_msg_group_layout = QtWidgets.QHBoxLayout(self.top_msg_group)
        self.option_msg_label = QtWidgets.QLabel('Make a task selection to view options')
        _option_icon_label = QtWidgets.QLabel()
        _icon = qtawesome.icon("fa.exclamation-circle", color="#c6c6c6")
        _pixmap = _icon.pixmap(18, 18)
        _option_icon_label.setPixmap(_pixmap)
        top_msg_group_layout.addWidget(_option_icon_label, 0)
        top_msg_group_layout.addWidget(self.option_msg_label, 0)
        self.tasks_option_layout.addWidget(self.top_msg_group, 1)

        # Generate option widget
        self.project = avalon.io.find_one({"name": avalon.api.Session["AVALON_PROJECT"], "type": "project"})
        self.assets = avalon.io.find({"type": "asset"})

        self.options_tasks_data = {}
        for _asset in self.assets:
            asset_name = _asset['name']
            asset_tasks = _asset['data'].get('tasks', '')
            if asset_tasks:
                self.options_tasks_data[asset_name] = {}
                for _task_data in self.project['config']['tasks']:
                    if 'options' in _task_data.keys() and _task_data['name'] in asset_tasks:
                        self.options_tasks_data[asset_name][_task_data['name']] = copy.deepcopy(_task_data['options'])  # _task_data['options']

        for asset_name, task_data in self.options_tasks_data.items():
            for _task_name, _options in task_data.items():
                _option_group = QtWidgets.QGroupBox(asset_name)
                _option_group.hide()
                _option_layout = QtWidgets.QVBoxLayout(_option_group)
                for _option_name, _data in _options.items():
                    if _option_name == 'widget':
                        continue
                    _default_value = _data['default_value']
                    if type(_default_value) == bool:
                        options = [
                            qargparse.Boolean(_option_name,
                                              label=_data['label'], default=_default_value, help=_data.get('help', ''))
                        ]
                        self.__set_option_widget(options, asset_name, _option_name, _task_name, _option_layout)

                    if type(_default_value) == int:
                        options = [
                            qargparse.Integer(_option_name, label=_data['label'],
                                              default=_default_value,
                                              max=_data.get('max', 99),
                                              min=_data.get('min', 0),
                                              write=8,
                                              help=_data.get('help', ''))
                        ]

                        self.__set_option_widget(options, asset_name, _option_name, _task_name, _option_layout)

                _options['widget'] = _option_group
                self.tasks_option_layout.addWidget(_option_group, 1)

        spacerItem = QtWidgets.QSpacerItem(20, 900, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.tasks_option_layout.addItem(spacerItem)

        # set layout
        tasks_layout.addWidget(label, 0, 0)
        tasks_layout.addWidget(option_top_label, 0, 1)
        tasks_layout.addWidget(task_view, 1, 0)
        tasks_layout.addWidget(self.tasks_option_view, 1, 1)
        tasks_layout.addWidget(add_task, 2, 0, 1, 2)

        body = QtWidgets.QSplitter()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        body.setOrientation(QtCore.Qt.Horizontal)
        body.addWidget(assets_widgets)
        body.addWidget(tasks_widgets)
        body.setStretchFactor(0, 50)
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
        task_view.selectionModel().selectionChanged.connect(self.on_task_changed)

        self.resize(800, 500)

        self.echo("Connected to project: {0}".format(project_name))

    def __set_option_widget(self, options, asset_name, option_name, task_name, option_layout):
        parser = qargparse.QArgumentParser(arguments=options)

        # Set value
        _filter = {"type": "asset", "name": asset_name}
        option_data = io.find(_filter, projection={"data.task_options": True})
        for _datas in option_data:
            value = _datas['data'].get('task_options', {}).get(task_name, {}).get(option_name, {}).get('value', '')
            if value:
                parser._arguments[option_name].write(value)

        # Set connection
        parser.changed.connect(partial(self.on_changed, task_name=task_name))
        option_layout.addWidget(parser)

    def on_changed(self, argument, task_name=''):
        # self._options[argument["name"]] = argument.read()
        option_name = argument["name"]
        option_value = argument.read()

        # Get selection asset name
        model = self.data["model"]["assets"]
        self.asset_selected = model.get_selected_assets()
        sel_asset_name = self.asset_selected[0]['data']['label']

        asset = io.find_one({"type": "asset", "name": sel_asset_name})
        asset_id = asset["_id"]

        filter_ = {"_id": asset_id}
        value_dict = {
            'value': option_value
        }
        update = {"$set": {
            "data.task_options.{}.{}".format(task_name, option_name): value_dict}
        }
        io.update_many(filter_, update)

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
        self.data["model"]["tasks"].set_assets(selected)

        self._hide_task_options()
        self.top_msg_group.show()
        self.option_msg_label.setText('Make a task selection to view options')

    def _hide_task_options(self):
        for _asset_name, _data in self.options_tasks_data.items():
            for _, _op_data in _data.items():
                if 'widget' in _op_data.keys():
                    _op_data['widget'].hide()

    def on_task_changed(self, selected, deselected):
        """
        Callback on task selection changed.

        This updates the task extra option view.
        """
        tasks_model = self.data["model"]["tasks"]

        model = self.data["model"]["assets"]
        self.asset_selected = model.get_selected_assets()
        sel_asset_name = self.asset_selected[0]['data']['label']

        indexes = []
        for index in selected.indexes():
            if index.column() == 0:
                indexes.append(index)

        task_name = tasks_model.data(indexes[0], 0)

        self._hide_task_options()

        _option_data = self.options_tasks_data[sel_asset_name]
        if task_name in _option_data.keys():
            widget = _option_data[task_name].get('widget', '')
            if widget:
                widget.show()
                self.top_msg_group.hide()
        else:
            self.top_msg_group.show()
            self.option_msg_label.setText('No task options found')


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
