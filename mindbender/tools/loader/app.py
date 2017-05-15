import os
import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import api, io
from .. import lib

module = sys.modules[__name__]
module.window = None
module.root = api.registered_root()
module.project = os.getenv("MINDBENDER_PROJECT")

# Custom roles
DocumentRole = QtCore.Qt.UserRole + 1
RepresentationsRole = QtCore.Qt.UserRole + 2
LatestRole = QtCore.Qt.UserRole + 3


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
        subsets.setSelectionMode(subsets.ExtendedSelection)

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
        subsets.itemSelectionChanged.connect(self.on_subsetschanged)
        versions.currentItemChanged.connect(self.on_versionschanged)
        representations.currentItemChanged.connect(
            self.on_representationschanged)

        # Defaults
        self.resize(1100, 600)

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

        project = io.ObjectId(os.environ["MINDBENDER__PROJECT"])
        assets = io.find({"type": "asset", "parent": project})
        for asset in sorted(assets, key=lambda i: i["name"]):
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
        assets_model.setCurrentRow(0)
        self.data["button"]["load"].hide()
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

        for child in io.find({"type": "subset",
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

        if len(subsets_model.selectedItems()) > 1:
            item = QtWidgets.QListWidgetItem("Latest")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            item.setData(LatestRole, True)
            versions_model.addItem(item)
            versions_model.setCurrentItem(item)

        else:
            subset_item = subsets_model.currentItem()
            document = subset_item.data(DocumentRole)

            has = {"children": False}

            for child in io.find({"type": "version",
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

        # Item is disabled
        representations = {}

        if version_item.data(LatestRole):
            subsets = self.data["model"]["subsets"].selectedItems()
            subsets = list(item.data(DocumentRole) for item in subsets)

            for subset in subsets:
                latest_version = io.find_one({
                    "type": "version",
                    "parent": subset["_id"]
                }, sort=[("name", -1)])

                if not latest_version:
                    # No version available
                    continue

                for representation in io.find({
                        "type": "representation",
                        "parent": latest_version["_id"]}):

                    name = representation["name"]

                    # TODO(marcus): These are permanently excluded
                    # for now, but look towards making this customisable.
                    if name in ("json", "source"):
                        continue

                    if name not in representations:
                        representations[name] = list()

                    representations[name].append(representation)

        elif version_item.data(QtCore.Qt.ItemIsEnabled):
            document = version_item.data(DocumentRole)
            representations = {
                representation["name"]: [representation]
                for representation in io.find({"type": "representation",
                                               "parent": document["_id"]})
                if representation["name"] not in ("json", "source")
            }

        else:
            return

        has = {"children": False}

        for name, documents in representations.items():
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(RepresentationsRole, documents)
            representations_model.addItem(item)
            has["children"] = True

        if not has["children"]:
            item = QtWidgets.QListWidgetItem("No representations found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            representations_model.addItem(item)

    def on_representationschanged(self, *args):
        button = self.data["button"]["load"]
        button.hide()

        item = self.data["model"]["representations"].currentItem()

        if item and item.data(QtCore.Qt.ItemIsEnabled):
            button.show()
            button.setEnabled(True)

    def on_refresh_pressed(self):
        self.refresh()

    def on_stop_pressed(self):
        button = self.data["button"]["stop"]
        button.setText("Stopping..")
        button.setEnabled(False)

        self.data["state"]["running"] = False

    def on_load_pressed(self):
        models = self.data["model"]
        representations_model = models["representations"]
        representation_item = representations_model.currentItem()

        if representation_item is None:
            return

        for document in representation_item.data(RepresentationsRole):
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

            if self.data["button"]["autoclose"].checkState():
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

    try:
        module.window.close()
        del module.window
    except (RuntimeError, AttributeError):
        pass

    try:
        widgets = QtWidgets.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets["MayaWindow"]
    except KeyError:
        parent = None

    if debug:
        io.install()
        project = io.find_one({"type": "project", "name": "hulk"})
        os.environ["MINDBENDER__PROJECT"] = str(project["_id"])

    with lib.application():
        window = Window(parent)
        window.show()

        window.refresh()

        module.window = window
