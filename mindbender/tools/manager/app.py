import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import api, schema
from .. import lib


self = sys.modules[__name__]
self._window = None

# Custom roles
ContainerRole = QtCore.Qt.UserRole + 1
VersionRole = QtCore.Qt.UserRole + 2
ResultRole = QtCore.Qt.UserRole + 3


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

    def __init__(self, ls, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Container Manager")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

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
        autoclose_checkbox.setCheckState(QtCore.Qt.Checked)
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

        self.ls = ls
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

        for asset in api.ls(silos=[container["silo"]]):
            if asset["name"] != container["asset"]:
                continue

            for subset in asset["subsets"]:
                if subset["name"] != container["subset"]:
                    continue

                for version in sorted(subset["versions"], reverse=True):
                    name = api.format_version(version["version"])
                    item = QtWidgets.QListWidgetItem(name)

                    item.setData(QtCore.Qt.ItemIsEnabled, True)
                    item.setData(VersionRole, version)

                    versions_model.addItem(item)

                    # Indicate which model is currently loaded.
                    if version["version"] == container["version"]:
                        versions_model.setCurrentItem(item)

                    # Create data ready for `host.load()`
                    result = {
                        "schema": "mindbender-core:result-1.0",
                        "asset": asset,
                        "subset": subset,
                        "version": version,
                        "representation": None
                    }

                    # Make sure the data we make is coherent
                    # with its corresponding schema.
                    schema.validate(result, "result")

                    item.setData(ResultRole, result)

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
        transition = "'%s' from version %s -> %s" % (
            container["name"],
            container["version"],
            version["version"]
        )

        if container["version"] == version["version"]:
            load.hide()

        elif container["version"] > version["version"]:
            load.setText("Downgrade %s" % transition)
            load.show()

        else:
            load.setText("Upgrade %s" % transition)
            load.show()

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

        for container in self.ls():
            has["containers"] = True

            name = "{name}\t({subset})".format(**container)
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
            api.registered_host().remove(container)

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
        result = version_item.data(ResultRole)

        try:
            print(
                "Loading version"
                "{version[version]} of "
                "'{asset[name]}/{subset[name]}'"
                .format(**result)
            )

            api.registered_host().update(
                container=container,
                # asset=result["asset"],
                # subset=result["subset"],

                # Version is not an object, but the integer number
                version=result["version"]["version"]
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


def show(root=None, debug=False):
    """Display Loader GUI

    Arguments:
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    if self._window:
        self._window.close()
        del(self._window)

    try:
        widgets = QtWidgets.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets["MayaWindow"]
    except KeyError:
        parent = None

    def debug_ls():
        containers = [
            {
                "schema": "mindbender-core:container-1.0",
                "name": "Bruce01",
                "asset": "Bruce",
                "subset": "rigDefault",
                "version": 3,
                "silo": "assets",
            },
            {
                "schema": "mindbender-core:container-1.0",
                "name": "Bruce02",
                "asset": "Bruce",
                "subset": "modelDefault",
                "version": 2,
                "silo": "assets",
            }
        ]

        for container in containers:
            yield container

    # Debug fixture
    fixture = api.fixture(assets=["Bruce"],
                          subsets=["modelDefault", "rigDefault"],
                          versions=4)

    with fixture if debug else lib.dummy():
        with lib.application():
            window = Window(
                ls=debug_ls if debug else api.registered_host().ls,
                parent=parent
            )

            window.show()
            window.refresh()

            self._window = window
