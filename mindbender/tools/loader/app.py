import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import api
from .. import lib


self = sys.modules[__name__]
self._window = None

# Store previous results from api.ls()
self._cache = list()
self._use_cache = False

# This enables caching of results asset listing of the network.
# It means less strain on the network, but also that artists must
# not forget to hit the "refresh" button if there are new assets
# since they first opened the loader.
self._optimal_network_performance = False

# Custom roles
AssetRole = QtCore.Qt.UserRole + 1
SubsetRole = QtCore.Qt.UserRole + 2


class Window(QtWidgets.QDialog):
    """Basic asset loader interface

     _________________________________________
    |                                         |
    | Assets                                  |
    |  _____________________________________  |
    | |                  |                  | |
    | | Asset 1          | Subset 1         | |
    | | Asset 2          | Subset 2         | |
    | | ...              | ...              | |
    | |                  |                  | |
    | |                  |                  | |
    | |                  |                  | |
    | |                  |                  | |
    | |                  |                  | |
    | |                  |                  | |
    | |__________________|__________________| |
    |  _____________________________________  |
    | |                                     | |
    | |                Load                 | |
    | |_____________________________________| |
    |_________________________________________|

    """

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Asset Loader")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        container = QtWidgets.QWidget()

        assets = QtWidgets.QListWidget()
        subsets = QtWidgets.QListWidget()

        # Enable loading many subsets at once
        subsets.setSelectionMode(subsets.ExtendedSelection)

        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(assets)
        layout.addWidget(subsets)
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
        refresh_button = QtWidgets.QPushButton("Refresh")
        stop_button = QtWidgets.QPushButton("Searching..")
        stop_button.setToolTip("Click to stop searching")
        message = QtWidgets.QLabel()
        message.hide()

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(load_button)
        layout.addWidget(stop_button)
        layout.addWidget(refresh_button)
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

        # Defaults
        self.resize(320, 350)

        load_button.hide()
        stop_button.setFocus()

    def keyPressEvent(self, event):
        """Delegate keyboard events"""

        if event.key() == QtCore.Qt.Key_Return:
            return self.on_enter()

    def on_enter(self):
        self.on_load_pressed()

    def on_assetschanged(self, *args):
        assets_model = self.data["model"]["assets"]
        subsets_model = self.data["model"]["subsets"]

        subsets_model.clear()

        asset_item = assets_model.currentItem()

        # The model is empty
        if asset_item is None:
            return

        asset = asset_item.data(AssetRole)

        # The model contains an empty item
        if asset is None:
            return

        for subset in asset["subsets"]:
            item = QtWidgets.QListWidgetItem(subset["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(SubsetRole, subset)
            subsets_model.addItem(item)

    def on_subsetschanged(self, *args):
        button = self.data["button"]["load"]
        item = self.data["model"]["assets"].currentItem()
        button.setEnabled(item.data(QtCore.Qt.ItemIsEnabled))

    def refresh(self):
        """Load assets from disk and add them to a QListView

        This method runs part-asynchronous, in that it blocks
        when busy, but takes brief intermissions between each
        asset found so as to lighten the load off of disk, and
        to enable the artist to abort searching once the target
        asset has been found.

        """

        assets_model = self.data["model"]["assets"]
        assets_model.clear()

        state = self.data["state"]

        if not api.registered_root():
            item = QtWidgets.QListWidgetItem("No root registered.")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            state["running"] = False

            assets_model.setFocus()
            # self.data["button"]["load"].show()
            self.data["button"]["stop"].hide()

            return assets_model.addItem(item)

        has = {"assets": False}

        module = sys.modules[__name__]
        if module._optimal_network_performance and module._use_cache:
            print("Using cache..")
            iterator = iter(module._cache)

        else:
            print("Reading from disk..")
            iterator = api.ls(silos=["assets", "film"])

        def on_next():
            if not state["running"]:
                return on_finished()

            try:
                asset = next(iterator)

                # Cache for re-use
                if not module._use_cache:
                    module._cache.append(asset)

            except StopIteration:
                return on_finished()

            has["assets"] = True

            item = QtWidgets.QListWidgetItem(asset["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(AssetRole, asset)
            assets_model.addItem(item)

            lib.defer(25, on_next)

        def on_finished():
            state["running"] = False
            module._use_cache = True

            if not has["assets"]:
                item = QtWidgets.QListWidgetItem("No assets found")
                item.setData(QtCore.Qt.ItemIsEnabled, False)
                assets_model.addItem(item)

            assets_model.setFocus()
            self.data["button"]["load"].show()
            self.data["button"]["stop"].hide()

        state["running"] = True
        lib.defer(25, on_next)

    def on_refresh_pressed(self):
        # Clear cache
        sys.modules[__name__]._cache[:] = []
        sys.modules[__name__]._use_cache = False

        self.refresh()

    def on_stop_pressed(self):
        button = self.data["button"]["stop"]
        button.setText("Stopping..")
        button.setEnabled(False)

        self.data["state"]["running"] = False

    def on_load_pressed(self):
        button = self.data["button"]["load"]
        if not button.isEnabled():
            return

        assets_model = self.data["model"]["assets"]
        subsets_model = self.data["model"]["subsets"]
        autoclose_checkbox = self.data["button"]["autoclose"]

        asset_item = assets_model.currentItem()

        for subset_item in subsets_model.selectedItems():

            if subset_item is None:
                return

            asset = asset_item.data(AssetRole)
            subset = subset_item.data(SubsetRole)
            assert asset
            assert subset

            try:
                api.registered_host().load(asset, subset)

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

    if self._window:
        self._window.close()
        del(self._window)

    try:
        widgets = QtWidgets.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets["MayaWindow"]
    except KeyError:
        parent = None

    # Debug fixture
    fixture = api.fixture(assets=["Ryan",
                                  "Strange",
                                  "Blonde_model"])

    with fixture if debug else lib.dummy():
        with lib.application():
            window = Window(parent)
            window.show()

            window.refresh()

            self._window = window
