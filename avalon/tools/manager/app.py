import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import api, io, style
from .. import lib

module = sys.modules[__name__]
module.window = None

# Custom roles
ContainerRole = QtCore.Qt.UserRole + 1
SubsetRole = QtCore.Qt.UserRole + 2
VersionRole = QtCore.Qt.UserRole + 3
CurrentVersionRole = QtCore.Qt.UserRole + 4
RepresentationRole = QtCore.Qt.UserRole + 5


class Window(QtWidgets.QDialog):
    """Basic container loader interface

     _________________________________________
    |                                         |
    | Containers                              |
    |  _____________________________________  |
    | |                         |           | |
    | | Container 1             | Version 1 | |
    | | Container 2             | Version 2 | |
    | | ...                     | ...       | |
    | |                         |           | |
    | |                         |           | |
    | |                         |           | |
    | |                         |           | |
    | |                         |           | |
    | |                         |           | |
    | |_________________________|___________| |
    |  _____________________________________  |
    | |                                     | |
    | |                Load                 | |
    | |_____________________________________| |
    |_________________________________________|

    """

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Container Manager")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        container = QtWidgets.QWidget()

        containers = QtWidgets.QListWidget()
        versions = QtWidgets.QListWidget()

        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(containers, 2)
        layout.addWidget(versions, 1)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)

        autoclose_checkbox = QtWidgets.QCheckBox("Auto-close")
        layout.addWidget(autoclose_checkbox, 1, 0)

        layout = QtWidgets.QVBoxLayout(body)
        layout.addWidget(container)
        layout.addWidget(options, 0, QtCore.Qt.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)

        load_button = QtWidgets.QPushButton("Load")
        remove_button = QtWidgets.QPushButton("Remove")
        remove_button.setAttribute(QtCore.Qt.WA_StyledBackground)
        remove_button.setStyleSheet("""
            QPushButton {
                background: #e04c4c;
                border: 1px solid #ff0000;
                height: 20px;
            }
        """)

        layout = QtWidgets.QHBoxLayout(footer)
        layout.addWidget(load_button)
        layout.addWidget(remove_button)
        layout.setContentsMargins(0, 0, 0, 0)

        message = QtWidgets.QLabel()

        statusbar = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(statusbar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(message)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)
        layout.addWidget(statusbar)

        self.data = {

            # Is the user working with the container,
            # or a particular version?
            "mode": "container",

            "button": {
                "load": load_button,
                "remove": remove_button,
                "autoclose": autoclose_checkbox,
            },
            "model": {
                "containers": containers,
                "versions": versions,
            },
            "label": {
                "message": message,
            }
        }

        load_button.clicked.connect(self.on_load_pressed)
        remove_button.clicked.connect(self.on_remove_pressed)
        containers.currentItemChanged.connect(self.on_containerschanged)
        containers.pressed.connect(self.on_focuschanged)
        versions.currentItemChanged.connect(self.on_versionschanged)
        versions.pressed.connect(self.on_focuschanged)

        # Defaults
        load_button.hide()
        remove_button.hide()
        self.resize(400, 350)

        load_button.setFocus()

    def on_focuschanged(self, *args):
        containers_model = self.data["model"]["containers"]
        versions_model = self.data["model"]["versions"]
        load = self.data["button"]["load"]
        remove = self.data["button"]["remove"]

        container_item = containers_model.currentItem()
        container = container_item.data(ContainerRole)

        if not container_item.data(QtCore.Qt.ItemIsEnabled):
            return

        if containers_model.hasFocus():
            remove.setText("Remove %s" % container["name"])
            remove.show()
            load.hide()

        if versions_model.hasFocus():
            remove.hide()

    def refresh(self):
        """Load containers from disk and add them to a QListView

        This method runs part-asynchronous, in that it blocks
        when busy, but takes brief intermissions between each
        container found so as to lighten the load off of disk, and
        to enable the artist to abort searching once the target
        container has been found.

        """

        containers_model = self.data["model"]["containers"]
        containers_model.clear()

        has = {"containers": False}

        for container in api.registered_host().ls():
            has["containers"] = True

            if container["schema"] == "avalon-core:container-1.0":
                name = container["objectName"]
                container["representation"] = str(io.locate([
                    api.Session["AVALON_PROJECT"],
                    container["asset"],
                    container["subset"],
                    container["version"],
                    container["representation"].strip("."),
                ]))

            else:
                name = "{namespace}{name}".format(**container)

            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(ContainerRole, container)
            containers_model.addItem(item)

        if not has["containers"]:
            item = QtWidgets.QListWidgetItem("No containers found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            containers_model.addItem(item)

            containers_model.setFocus()
            self.data["button"]["load"].show()

        self.data["button"]["load"].hide()
        self.data["button"]["remove"].hide()

    def keyPressEvent(self, event):
        """Delegate keyboard events"""

        if event.key() == QtCore.Qt.Key_Return:
            return self.on_enter()

    def on_enter(self):
        containers_model = self.data["model"]["containers"]
        versions_model = self.data["model"]["versions"]

        if containers_model.hasFocus():
            self.on_remove_pressed()

        elif versions_model.hasFocus():
            self.on_load_pressed()

    def on_containerschanged(self, *args):
        containers_model = self.data["model"]["containers"]
        versions_model = self.data["model"]["versions"]
        button = self.data["button"]["load"]

        button.hide()
        versions_model.clear()

        container_item = containers_model.currentItem()

        # The model is empty
        if container_item is None:
            return

        container = container_item.data(ContainerRole)

        # The model contains an empty item
        if container is None:
            return

        current_representation = io.find_one({
            "_id": io.ObjectId(container["representation"])
        })

        current_version = io.find_one({
            "_id": current_representation["parent"]
        })

        current_subset = io.find_one({
            "_id": current_version["parent"]
        })

        all_versions = io.find({
            "type": "version",
            "parent": current_subset["_id"]
        })

        for version in sorted(all_versions,
                              key=lambda v: v["name"],
                              reverse=True):

            item = QtWidgets.QListWidgetItem("v%03d" % version["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(VersionRole, version)
            item.setData(CurrentVersionRole, current_version["name"])
            item.setData(SubsetRole, current_subset)

            versions_model.addItem(item)

            # Indicate which model is currently loaded.
            if current_version["name"] == version["name"]:
                versions_model.setCurrentItem(item)

    def on_versionschanged(self, *args):
        load = self.data["button"]["load"]
        containers_model = self.data["model"]["containers"]
        versions_model = self.data["model"]["versions"]

        container_item = containers_model.currentItem()
        version_item = versions_model.currentItem()

        # The model is empty
        if version_item is None:
            return

        container = container_item.data(ContainerRole)
        version = version_item.data(VersionRole)
        current_version = version_item.data(CurrentVersionRole)
        message = "'{0}' from version {1} -> {2}".format(
            container["name"], current_version, version["name"]
        )

        if current_version == version["name"]:
            load.hide()

        elif current_version > version["name"]:
            load.setText("Downgrade %s" % message)
            load.show()

        else:
            load.setText("Upgrade %s" % message)
            load.show()

    def on_remove_pressed(self):
        containers_model = self.data["model"]["containers"]
        container_item = containers_model.currentItem()
        container = container_item.data(ContainerRole)
        autoclose_checkbox = self.data["button"]["autoclose"]

        messagebox = QtWidgets.QMessageBox()
        messagebox.setIcon(messagebox.Warning)
        messagebox.setWindowTitle("Warning")
        messagebox.setText("Are you sure you would like to remove '%s'"
                           % container["name"])
        messagebox.setStandardButtons(messagebox.Yes | messagebox.No)
        messagebox.setDefaultButton(messagebox.No)

        if messagebox.exec_() == messagebox.Yes:

            self.echo("Removing '%s'.." % container["name"])
            api.remove(container)

            if autoclose_checkbox.checkState():
                self.close()
            else:
                self.refresh()

    def on_load_pressed(self):
        button = self.data["button"]["load"]
        if not button.isEnabled():
            return

        versions_model = self.data["model"]["versions"]
        containers_model = self.data["model"]["containers"]
        autoclose_checkbox = self.data["button"]["autoclose"]

        container_item = containers_model.currentItem()
        version_item = versions_model.currentItem()

        container = container_item.data(ContainerRole)
        version = version_item.data(VersionRole)

        try:
            print(
                "Updating {container} to '{version}'"
                .format(container=container["name"],
                        version=version["name"])
            )

            api.update(
                container=container,
                version=version["name"]
            )

        except ValueError as e:
            self.echo(e)
            raise

        except NameError as e:
            self.echo(e)
            raise

        # Catch-all
        except Exception as e:
            self.echo("Program error: %s" % str(e))
            raise

        if autoclose_checkbox.checkState():
            self.close()
        else:
            self.refresh()

    def echo(self, message):
        widget = self.data["label"]["message"]
        widget.setText(str(message))

        QtCore.QTimer.singleShot(5000, lambda: widget.setText(""))

        print(message)

    def closeEvent(self, event):
        print("Good bye")
        return super(Window, self).closeEvent(event)


def show(root=None, debug=False, parent=None):
    """Display Loader GUI

    Arguments:
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    try:
        module.window.close()
        del module.window
    except (RuntimeError, AttributeError):
        pass

    if debug is True:
        io.install()

        any_project = next(
            project for project in io.projects()
            if project.get("active", True) is not False
        )

        api.Session["AVALON_PROJECT"] = any_project["name"]

    with lib.application():
        window = Window(parent)
        window.setStyleSheet(style.load_stylesheet())
        window.show()
        window.refresh()

        module.window = window
