import os
import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import api
from .. import lib

# Third-party dependencies
import pymongo
from bson.objectid import ObjectId

module = sys.modules[__name__]
module.window = None
module.io = None
module.root = api.registered_root()
module.project = os.getenv("MINDBENDER_PROJECT")

# Custom roles
DocumentRole = QtCore.Qt.UserRole + 1


class Window(QtWidgets.QDialog):
    """Asset loader interface"""

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle(
            "Asset Loader 2.0 - %s/%s" % (
                module.root, module.project))

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        body = QtWidgets.QWidget()
        sidepanel = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        container = QtWidgets.QWidget()

        assets = QtWidgets.QListWidget()
        subsets = QtWidgets.QListWidget()
        versions = QtWidgets.QListWidget()
        representations = QtWidgets.QListWidget()

        # Enable loading many subsets at once
        # subsets.setSelectionMode(subsets.ExtendedSelection)
        # versions.setSelectionMode(subsets.ExtendedSelection)
        # representations.setSelectionMode(subsets.ExtendedSelection)

        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(assets)
        layout.addWidget(subsets)
        layout.addWidget(versions)
        layout.addWidget(representations)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)

        autoclose_checkbox = QtWidgets.QCheckBox("Auto-close")
        autoclose_checkbox.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(autoclose_checkbox, 1, 0)

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(container)
        layout.addWidget(sidepanel)
        layout.setContentsMargins(0, 0, 0, 0)

        load_button = QtWidgets.QPushButton("Load")
        refresh_button = QtWidgets.QPushButton("Refresh")
        stop_button = QtWidgets.QPushButton("Searching..")
        stop_button.setToolTip("Click to stop searching")
        message = QtWidgets.QLabel()
        message.hide()

        layout = QtWidgets.QVBoxLayout(sidepanel)
        layout.addWidget(load_button)
        layout.addWidget(stop_button)
        layout.addWidget(refresh_button)
        layout.addWidget(options, 0, QtCore.Qt.AlignBottom)
        layout.addWidget(QtWidgets.QWidget(), 1)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(message)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.data = {
            "state": {
                "running": False,
            },
            "button": {
                "load": load_button,
                "stop": stop_button,
                "autoclose": autoclose_checkbox,
            },
            "model": {
                "assets": assets,
                "subsets": subsets,
                "versions": versions,
                "representations": representations
            },
            "label": {
                "message": message,
            }
        }

        load_button.clicked.connect(self.on_load_pressed)
        stop_button.clicked.connect(self.on_stop_pressed)
        refresh_button.clicked.connect(self.on_refresh_pressed)
        assets.currentItemChanged.connect(self.on_assetschanged)
        subsets.currentItemChanged.connect(self.on_subsetschanged)
        versions.currentItemChanged.connect(self.on_versionschanged)
        representations.currentItemChanged.connect(
            self.on_representationschanged)

        # Defaults
        self.resize(620, 350)

        load_button.hide()
        stop_button.setFocus()

    def keyPressEvent(self, event):
        """Delegate keyboard events"""

        if event.key() == QtCore.Qt.Key_Return:
            return self.on_enter()

    def on_enter(self):
        self.on_load_pressed()

    def refresh(self):
        """Load assets from disk and add them to a QListView"""

        assets_model = self.data["model"]["assets"]
        assets_model.clear()

        has = {"children": False}

        project = ObjectId(os.environ["MINDBENDER__PROJECT"])
        for asset in module.io.find({"type": "asset", "parent": project}):
            item = QtWidgets.QListWidgetItem(asset["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(DocumentRole, asset)
            assets_model.addItem(item)
            has["children"] = True

        if not has["children"]:
            item = QtWidgets.QListWidgetItem("No assets found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            assets_model.addItem(item)

        assets_model.setFocus()
        self.data["button"]["load"].show()
        self.data["button"]["stop"].hide()

    def on_assetschanged(self, *args):
        assets_model = self.data["model"]["assets"]
        subsets_model = self.data["model"]["subsets"]

        subsets_model.clear()

        asset_item = assets_model.currentItem()

        # The model is empty
        if asset_item is None:
            return

        document = asset_item.data(DocumentRole)

        # The model contains an empty item
        if document is None:
            return

        has = {"children": False}

        for child in module.io.find({"type": "subset",
                                     "parent": document["_id"]}):
            item = QtWidgets.QListWidgetItem(child["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(DocumentRole, child)
            subsets_model.addItem(item)
            has["children"] = True

        if not has["children"]:
            item = QtWidgets.QListWidgetItem("No subsets found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            subsets_model.addItem(item)

    def on_subsetschanged(self, *args):
        subsets_model = self.data["model"]["subsets"]
        versions_model = self.data["model"]["versions"]

        versions_model.clear()

        subset_item = subsets_model.currentItem()

        # The model is empty
        if subset_item is None:
            return

        document = subset_item.data(DocumentRole)

        has = {"children": False}

        for child in module.io.find({"type": "version",
                                     "parent": document["_id"]}):
            item = QtWidgets.QListWidgetItem("v%03d" % child["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(DocumentRole, child)
            versions_model.addItem(item)
            has["children"] = True

        if not has["children"]:
            item = QtWidgets.QListWidgetItem("No versions found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            versions_model.addItem(item)

    def on_versionschanged(self, *args):
        versions_model = self.data["model"]["versions"]
        representations_model = self.data["model"]["representations"]

        representations_model.clear()

        version_item = versions_model.currentItem()

        # The model is empty
        if version_item is None:
            return

        document = version_item.data(DocumentRole)

        has = {"children": False}

        for child in module.io.find({"type": "representation",
                                     "parent": document["_id"]}):
            label = child.get("label") or child["name"]
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(DocumentRole, child)
            representations_model.addItem(item)
            has["children"] = True

        if not has["children"]:
            item = QtWidgets.QListWidgetItem("No representations found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            representations_model.addItem(item)

    def on_representationschanged(self, *args):
        button = self.data["button"]["load"]
        item = self.data["model"]["assets"].currentItem()
        button.setEnabled(item.data(QtCore.Qt.ItemIsEnabled))

    def on_refresh_pressed(self):
        self.refresh()

    def on_stop_pressed(self):
        button = self.data["button"]["stop"]
        button.setText("Stopping..")
        button.setEnabled(False)

        self.data["state"]["running"] = False

    def on_load_pressed(self):
        autoclose_checkbox = self.data["button"]["autoclose"]
        button = self.data["button"]["load"]
        if not button.isEnabled():
            return

        representations_model = self.data["model"]["representations"]
        representation_item = representations_model.currentItem()

        if representation_item is None:
            return

        document = representation_item.data(DocumentRole)

        try:
            api.registered_host().load(representation=document["_id"])

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

    def echo(self, message):
        widget = self.data["label"]["message"]
        widget.setText(str(message))
        widget.show()
        print(message)

    def closeEvent(self, event):
        print("Good bye")
        self.data["state"]["running"] = False
        return super(Window, self).closeEvent(event)


def show(root=None, debug=False):
    """Display Loader GUI

    Arguments:
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    uri = os.environ["MINDBENDER_MONGO"]
    client = pymongo.MongoClient(uri)
    database = client["mindbender"]
    collection = database["assets"]

    assert client.server_info()
    print(client.server_info())

    module.io = collection

    try:
        module.window.close()
    except (RuntimeError, AttributeError):
        pass

    try:
        widgets = QtWidgets.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets["MayaWindow"]
    except KeyError:
        parent = None

    with lib.application():
        window = Window(parent)
        window.show()

        window.refresh()

        module.window = window
