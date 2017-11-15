import avalon

from avalon.vendor.Qt import QtWidgets, QtCore
from avalon.tools.projectmanager.widget import AssetWidget
from avalon.tools.projectmanager.app import TasksModel


class App(QtWidgets.QDialog):
    """Context manager window"""

    def __init__(self, project=None, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        _project = avalon.Session.get("AVALON_PROJECT", project)
        asset = avalon.Session.get("AVALON_ASSET", "Asset")
        task = avalon.Session.get("AVALON_TASK", "Task")

        self.resize(680, 360)
        self.setWindowTitle("Context Manager 1.0 - {}".format(_project))
        self.setObjectName("contextManager")

        layout = QtWidgets.QVBoxLayout(self)
        column_layout = QtWidgets.QHBoxLayout()

        # Asset picker
        assets = AssetWidget()

        # Task picker
        tasks_widgets = QtWidgets.QWidget()
        tasks_widgets.setContentsMargins(0, 0, 0, 0)
        tasks_layout = QtWidgets.QVBoxLayout(tasks_widgets)
        task_view = QtWidgets.QTreeView()
        task_view.setIndentation(0)
        task_model = TasksModel()
        task_view.setModel(task_model)
        tasks_layout.addWidget(task_view)

        # region results
        result_widget = QtWidgets.QWidget()
        result_widget.setFixedWidth(200)
        result_layout = QtWidgets.QVBoxLayout()
        result_widget.setLayout(result_layout)

        project_label = QtWidgets.QLabel("Project")
        project_value = QtWidgets.QLineEdit(_project)
        project_value.setReadOnly(True)
        project_label.setBuddy(project_value)

        asset_label = QtWidgets.QLabel("Asset")
        asset_value = QtWidgets.QLineEdit(asset)
        asset_value.setReadOnly(True)
        asset_label.setBuddy(asset_value)

        task_label = QtWidgets.QLabel("Task")
        task_value = QtWidgets.QLineEdit(task)
        task_value.setReadOnly(True)
        task_label.setBuddy(task_value)

        accept = QtWidgets.QPushButton("Accept")

        result_layout.addWidget(project_label)
        result_layout.addWidget(project_value)
        result_layout.addWidget(asset_label)
        result_layout.addWidget(asset_value)
        result_layout.addWidget(task_label)
        result_layout.addWidget(task_value)
        result_layout.insertSpacing(6, 150)
        result_layout.addWidget(accept)
        # endregion results

        column_layout.addWidget(assets)
        column_layout.addWidget(tasks_widgets)
        column_layout.addWidget(result_widget)

        layout.addLayout(column_layout)
        task_selection_model = task_view.selectionModel()

        self.data = {
            "preview": {"asset": asset_value,
                        "task": task_value},
            "view": {"tasks": task_view},
            "model": {
                "assets": assets,
                "tasks": task_model,
            }
        }

        assets.selection_changed.connect(self.on_asset_changed)
        task_selection_model.selectionChanged.connect(self.preview_result)
        assets.refresh()

        self.setLayout(layout)

        accept.clicked.connect(self.on_accept_clicked)

    def on_asset_changed(self):
        """Callback on asset selection changed

        This updates the task view.

        """

        model = self.data["model"]["assets"]
        selected = model.get_selected_assets()
        self.data['model']['tasks'].set_assets(selected)

    def preview_result(self):

        NodeRole = QtCore.Qt.UserRole + 1

        assets_model = self.data["model"]["assets"]
        task_view = self.data["view"]["tasks"]

        asset_index = assets_model.view.currentIndex()
        asset = asset_index.data(NodeRole)
        task_index = task_view.currentIndex()
        task = task_index.data(NodeRole)

        asset_name = asset["name"]
        task_name = task["name"]

        self.data["preview"]["asset"].setText(asset_name)
        self.data["preview"]["task"].setText(task_name)

    def on_accept_clicked(self):

        task = self.data["preview"]["task"].text()
        asset = self.data["preview"]["asset"].text()

        print asset, task


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    test = App("TESTCASE")
    test.show()
    app.exec_()
