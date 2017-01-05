import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import api
from .. import lib


self = sys.modules[__name__]
self._window = None


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

        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(assets)
        layout.addWidget(subsets)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)

        autoclose_checkbox = QtWidgets.QCheckBox("Close after load")
        autoclose_checkbox.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(autoclose_checkbox, 1, 0)

        layout = QtWidgets.QVBoxLayout(body)
        layout.addWidget(container)
        layout.addWidget(options, 0, QtCore.Qt.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)

        load_button = QtWidgets.QPushButton("Load")
        stop_button = QtWidgets.QPushButton("Searching..")
        stop_button.setToolTip("Click to stop searching")
        message = QtWidgets.QLabel()
        message.hide()

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(load_button)
        layout.addWidget(stop_button)
        layout.addWidget(message)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.data = {
            "state": {
                "running": False
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

        load_button.clicked.connect(self.on_load)
        stop_button.clicked.connect(self.on_stop)
        assets.currentItemChanged.connect(self.on_assetschanged)
        subsets.currentItemChanged.connect(self.on_subsetschanged)

        # Defaults
        self.resize(220, 250)
        load_button.hide()
        stop_button.setFocus()

    def keyPressEvent(self, event):
        """Delegate keyboard events"""

        if event.key() == QtCore.Qt.Key_Return:
            return self.on_enter()

    def on_enter(self):
        self.on_load()

    def on_assetschanged(self, *args):
        assets_model = self.data["model"]["assets"].currentItem()
        subsets_model = self.data["model"]["subsets"]

        subsets_model.clear()

        for subset in assets_model.data(AssetRole)["subsets"]:
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
        state = self.data["state"]

        has = {"assets": False}
        assets = api.ls()

        def on_next():
            if not state["running"]:
                return on_finished()

            try:
                asset = next(assets)
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

            if not has["assets"]:
                item = QtWidgets.QListWidgetItem("No assets found")
                item.setData(QtCore.Qt.ItemIsEnabled, False)
                assets_model.addItem(item)

            assets_model.setCurrentItem(assets_model.item(0))
            assets_model.setFocus()
            self.data["button"]["load"].show()
            self.data["button"]["stop"].hide()

        state["running"] = True
        lib.defer(25, on_next)

    def on_stop(self):
        button = self.data["button"]["stop"]
        button.setText("Stopping..")
        button.setEnabled(False)

        self.data["state"]["running"] = False

    def on_load(self):
        button = self.data["button"]["load"]
        if not button.isEnabled():
            return

        subsets_model = self.data["model"]["subsets"]
        autoclose_checkbox = self.data["button"]["autoclose"]

        item = subsets_model.currentItem()

        if item is not None:
            subset = item.data(SubsetRole)
            assert subset

            try:
                api.registered_host().load(subset)

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

    def closeEvent(self, event):
        self.data["state"]["running"] = False
        super(Window, self).closeEvent(event)


def show(debug=False):
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
