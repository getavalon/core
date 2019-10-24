import sys
import logging

from ... import api

from ...vendor.Qt import QtWidgets, QtCore
from ..widgets import AssetWidget
from ..models import TasksModel

module = sys.modules[__name__]
module.window = None


log = logging.getLogger(__name__)


class App(QtWidgets.QDialog):
    """Context manager window"""

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.resize(640, 360)
        project = api.Session["AVALON_PROJECT"]
        self.setWindowTitle("Context Manager 1.0 - {}".format(project))
        self.setObjectName("contextManager")

        splitter = QtWidgets.QSplitter(self)
        main_layout = QtWidgets.QVBoxLayout()
        column_layout = QtWidgets.QHBoxLayout()

        accept_btn = QtWidgets.QPushButton("Accept")

        # Asset picker
        assets = AssetWidget(silo_creatable=False)

        # Task picker
        tasks_widgets = QtWidgets.QWidget()
        tasks_widgets.setContentsMargins(0, 0, 0, 0)
        tasks_layout = QtWidgets.QVBoxLayout(tasks_widgets)
        task_view = QtWidgets.QTreeView()
        task_view.setIndentation(0)
        task_model = TasksModel()
        task_view.setModel(task_model)
        tasks_layout.addWidget(task_view)
        tasks_layout.addWidget(accept_btn)
        task_view.setColumnHidden(1, True)

        # region results
        result_widget = QtWidgets.QGroupBox("Current Context")
        result_layout = QtWidgets.QVBoxLayout()
        result_widget.setLayout(result_layout)

        project_label = QtWidgets.QLabel("Project: {}".format(project))
        asset_label = QtWidgets.QLabel()
        task_label = QtWidgets.QLabel()

        result_layout.addWidget(project_label)
        result_layout.addWidget(asset_label)
        result_layout.addWidget(task_label)
        result_layout.addStretch()
        # endregion results

        context_widget = QtWidgets.QWidget()
        column_layout.addWidget(assets)
        column_layout.addWidget(tasks_widgets)
        context_widget.setLayout(column_layout)

        splitter.addWidget(context_widget)
        splitter.addWidget(result_widget)
        splitter.setSizes([1, 0])

        main_layout.addWidget(splitter)

        # Enable for other functions
        self._last_selected_task = None
        self._task_view = task_view
        self._task_model = task_model
        self._assets = assets
        self._accept_button = accept_btn

        self._context_asset = asset_label
        self._context_task = task_label

        assets.selection_changed.connect(self.on_asset_changed)
        accept_btn.clicked.connect(self.on_accept_clicked)
        task_view.selectionModel().selectionChanged.connect(
            self.on_task_changed)
        assets.assets_refreshed.connect(self.on_task_changed)
        assets.refresh()

        self.select_asset(api.Session["AVALON_ASSET"])
        self.select_task(api.Session["AVALON_TASK"])

        self.setLayout(main_layout)

        # Enforce current context to be up-to-date
        self.refresh_context_view()

    def refresh_context_view(self):
        """Refresh the context panel"""

        asset = api.Session.get("AVALON_ASSET", "")
        task = api.Session.get("AVALON_TASK", "")

        self._context_asset.setText("Asset: {}".format(asset))
        self._context_task.setText("Task: {}".format(task))

    def _get_selected_task_name(self):

        # Make sure we actually get the selected entry as opposed to the
        # active index. This way we know the task is actually selected and the
        # view isn't just active on something that is unselectable like
        # "No Task"
        selected = self._task_view.selectionModel().selectedRows()
        if not selected:
            return

        task_index = selected[0]
        return task_index.data(QtCore.Qt.DisplayRole)

    def _get_selected_asset_name(self):
        asset_index = self._assets.get_active_index()
        asset_data = asset_index.data(self._assets.model.ItemRole)
        if not asset_data or not isinstance(asset_data, dict):
            return

        return asset_data["name"]

    def on_asset_changed(self):
        """Callback on asset selection changed

        This updates the task view.

        """
        current_task_data = self._get_selected_task_name()
        if current_task_data:
            self._last_selected_task = current_task_data

        selected = self._assets.get_selected_assets()
        self._task_model.set_assets(selected)

        # Find task with same name
        if self._last_selected_task:
            self.select_task(self._last_selected_task)

        if not self._get_selected_task_name():
            # If no task got selected after the task model reset
            # then a "selection change" signal is not emitted.
            # As such we need to explicitly force the callback.
            self.on_task_changed()

    def on_task_changed(self):
        """Callback on task change."""

        # Toggle the "Accept" button enabled state
        asset = self._get_selected_asset_name()
        task = self._get_selected_task_name()
        if not asset or not task:
            self._accept_button.setEnabled(False)
        else:
            self._accept_button.setEnabled(True)

    def on_accept_clicked(self):
        """Apply the currently selected task to update current task"""

        asset_name = self._get_selected_asset_name()
        if not asset_name:
            log.warning("No asset selected.")
            return

        task_name = self._get_selected_task_name()
        if not task_name:
            log.warning("No task selected.")
            return

        api.update_current_task(task=task_name, asset=asset_name)
        self.refresh_context_view()

    def select_task(self, taskname):
        """Select task by name
        Args:
            taskname(str): name of the task to select

        Returns:
            None
        """

        parent = QtCore.QModelIndex()
        model = self._task_view.model()
        selectionmodel = self._task_view.selectionModel()

        for row in range(model.rowCount(parent)):
            idx = model.index(row, 0, parent)
            task = idx.data(QtCore.Qt.DisplayRole)
            if task == taskname:
                selectionmodel.select(idx,
                                      QtCore.QItemSelectionModel.Select)
                self._task_view.setCurrentIndex(idx)
                self._last_selected_task = taskname
                return

    def select_asset(self, assetname):
        """Select task by name
        Args:
            assetname(str): name of the task to select

        Returns:
            None
        """
        self._assets.select_assets([assetname], expand=True)


def show(parent=None):

    from avalon import style
    from ...tools import lib
    try:
        module.window.close()
        del module.window
    except (RuntimeError, AttributeError):
        pass

    with lib.application():
        window = App(parent)
        window.setStyleSheet(style.load_stylesheet())
        window.show()

        module.window = window
