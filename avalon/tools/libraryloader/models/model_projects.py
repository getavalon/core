from . import TreeModel
from .model_node import Node
from .... import style
from ....vendor import qtawesome as awesome
from ....vendor.Qt import QtCore


class ProjectsModel(TreeModel):
    """A model listing the tasks combined for a list of assets"""

    COLUMNS = ["name"]
    ObjectIdRole = QtCore.Qt.UserRole + 1

    def __init__(self, parent=None, show_projects=True, show_libraries=True):
        super(ProjectsModel, self).__init__(parent=parent)
        self.db = parent.db
        self.show_projects = show_projects
        self.show_libraries = show_libraries
        self._num_projects = 0
        self._icons = {
            "__default__": awesome.icon(
                "fa.map", color=style.colors.default
            )
        }
        self.set_context()

    def set_context(self):
        """Set projects from db

        """

        projects = list()
        for project in self.db.projects():
            name = project['name']
            if self.show_projects is True and self.show_libraries is True:
                projects.append(name)
            else:
                data = project.get('data', None)
                if data is None:
                    self.log.warning(
                        'Project "{}" don\'t have any "Data"'.format(name)
                    )
                is_library = data.get('library_project', False)
                if (
                    (self.show_libraries is True and is_library is True) or
                    (self.show_projects is True and is_library is False)
                ):
                    projects.append(name)

        self._num_projects = len(projects)

        self.clear()

        # TODO show user that no projects are available!!!
        if len(projects) == 0:
            return

        self.beginResetModel()

        icon = self._icons["__default__"]
        for project in sorted(projects):
            node = Node({
                "name": project,
                "icon": icon
            })

            self.add_child(node)

        self.endResetModel()

    def headerData(self, section, orientation, role):
        # Override header for count column to show amount of assets
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return "Project name"
        return super(ProjectsModel, self).headerData(
            section, orientation, role
        )

    def data(self, index, role):

        if not index.isValid():
            return

        # Add icon to the first column
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return index.internalPointer()['icon']

        return super(ProjectsModel, self).data(index, role)
