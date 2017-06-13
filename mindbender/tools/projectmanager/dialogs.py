from ... import io
from ...vendor import qtawesome as qta
from ...vendor.Qt import QtWidgets, QtCore
from . import lib


class TasksCreateDialog(QtWidgets.QDialog):
    """A Dialog to choose a list of Tasks to create."""

    def __init__(self, parent=None):
        super(TasksCreateDialog, self).__init__(parent=parent)
        self.setWindowTitle("Add Tasks")
        self.setModal(True)

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Select Tasks to create")

        tasks = lib.list_project_tasks()
        tasks = list(sorted(tasks))  # sort for readability
        list_widget = QtWidgets.QListWidget()
        list_widget.addItems(tasks)
        list_widget.setSelectionMode(list_widget.ExtendedSelection)

        footer = QtWidgets.QHBoxLayout()
        cancel = QtWidgets.QPushButton("Cancel")
        create = QtWidgets.QPushButton(qta.icon("fa.plus", color="grey"),
                                       "Create")
        footer.addWidget(create)
        footer.addWidget(cancel)

        layout.addWidget(label)
        layout.addWidget(list_widget)
        layout.addLayout(footer)

        cancel.clicked.connect(self.reject)
        cancel.setAutoDefault(False)

        create.clicked.connect(self.accept)
        create.setAutoDefault(True)

        self.list = list_widget

    def get_selected(self):
        """Return all selected task names

        Returns:
            list: Selected task names.

        """
        return [i.text() for i in self.list.selectedItems()]


class AssetCreateDialog(QtWidgets.QDialog):
    """A Dialog to create a new asset."""

    asset_created = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super(AssetCreateDialog, self).__init__(parent=parent)
        self.setWindowTitle("Add asset")

        self.parent_id = None
        self.parent_name = ""
        self.silo = ""

        # Label
        label_label = QtWidgets.QLabel("Label:")
        label = QtWidgets.QLineEdit()
        label.setPlaceholderText("<label>")

        # Parent
        parent_label = QtWidgets.QLabel("Parent:")
        parent_field = QtWidgets.QLineEdit()
        parent_field.setReadOnly(True)
        parent_field.setStyleSheet("background-color: #333333;")  # greyed out

        # Full name
        name_label = QtWidgets.QLabel("Name:")
        name = QtWidgets.QLineEdit()
        name.setReadOnly(True)
        name.setStyleSheet("background-color: #333333;")  # greyed out

        icon = qta.icon("fa.plus", color="grey")
        add_asset = QtWidgets.QPushButton(icon, "Add")
        add_asset.setAutoDefault(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label_label)
        layout.addWidget(label)
        layout.addWidget(parent_label)
        layout.addWidget(parent_field)
        layout.addWidget(name_label)
        layout.addWidget(name)
        layout.addWidget(add_asset)

        self.data = {
            "label": {
                "parent": parent_field,
                "label": label,
                "name": name
            }
        }

        # Force update the name field
        self.update_name()

        # Signals
        parent_field.textChanged.connect(self.update_name)
        label.textChanged.connect(self.update_name)
        add_asset.clicked.connect(self.on_add_asset)

    def set_silo(self, silo):
        assert silo
        self.silo = silo

    def set_parent(self, parent_id):

        # Get the parent asset (if any provided)
        parent_name = ""
        if parent_id:
            parent_asset = io.find_one({"_id": parent_id, "type": "asset"})
            assert parent_asset, "Parent asset does not exist."
            parent_name = parent_asset['name']

            self.parent_name = parent_name
            self.parent_id = parent_id
        else:
            # Clear the parent
            self.parent_name = ""
            self.parent_id = None

        self.data['label']['parent'].setText(parent_name)

    def update_name(self):
        """Force an update on the long name.
        
        The long name is based on the asset's label joined with
        the parent's full name.
        
        """

        label = self.data['label']['label'].text()
        name = label

        # Prefix with parent name (if parent)
        if self.parent_name:
            name = self.parent_name + "_" + name

        self.data['label']['name'].setText(name)

    def on_add_asset(self):

        parent_id = self.parent_id
        name = self.data['label']['name'].text()
        label = self.data['label']['label'].text()
        silo = self.silo

        assert name
        assert label
        assert silo

        data = {
            "name": name,
            "label": label,
            "silo": silo,
            "parent": parent_id
        }

        lib.create_asset(data)

        self.asset_created.emit(data)


# class CreateProjectDialog(QtWidgets.QDialog):
#     """A dialog to create a new project"""
#
#     def __init__(self, *args, **kwargs):
#         super(CreateProjectDialog, self).__init__(*args, **kwargs)
#         self.setWindowTitle("Create Project")
#         self.setModal(True)
#
#         layout = QtWidgets.QVBoxLayout(self)
#
#         self.label = QtWidgets.QLabel("Project name")
#         self.name = QtWidgets.QLineEdit()
#
#         self.projects_root_label = QtWidgets.QLabel("Projects directory")
#         self.projects_root = QtWidgets.QLineEdit()
#
#         footer = QtWidgets.QHBoxLayout()
#         create = QtWidgets.QPushButton("Create")
#         cancel = QtWidgets.QPushButton("Cancel")
#
#         footer.addWidget(create)
#         footer.addWidget(cancel)
#
#         layout.addWidget(self.label)
#         layout.addWidget(self.name)
#         layout.addWidget(self.projects_root_label)
#         layout.addWidget(self.projects_root)
#         layout.addLayout(footer)
#
#         cancel.clicked.connect(self.reject)
#         create.clicked.connect(self.accept)
#         self.accepted.connect(self.on_accept)
#
#     def on_accept(self):
#         """Perform creation of a new-style project"""
#
#         project_dir = self.projects_root.text()
#         project_name = self.name.text()
#
#         try:
#             self._create(project_dir, project_name)
#         except RuntimeError, e:
#             QtWidgets.QMessageBox.warning(self,
#                                           "Error creating Project",
#                                           str(e))
#
#     def _create(self, project_dir, project_name):
#
#
#         # Create the project
#         root = lib.create_project(project_name)
#
#         # Set the project bar
#         self.parent().projectBar.set_project(root)