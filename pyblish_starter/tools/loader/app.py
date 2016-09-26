import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import api
from .. import lib


self = sys.modules[__name__]
self._window = None


# Custom roles
AssetRole = QtCore.Qt.UserRole + 1


class Window(QtWidgets.QDialog):
    """Basic asset loader interface

     _________________________
    |                          |
    | Assets                   |
    |  ______________________  |
    | |                      | |
    | | Asset 1              | |
    | | Asset 2              | |
    | | ...                  | |
    | |                      | |
    | |                      | |
    | |                      | |
    | |                      | |
    | |                      | |
    | |                      | |
    | |______________________| |
    |  ______________________  |
    | |                      | |
    | |         Load         | |
    | |______________________| |
    |__________________________|

    """

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Asset Loader")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        container = QtWidgets.QWidget()

        listing = QtWidgets.QListWidget()

        layout = QtWidgets.QVBoxLayout(container)
        layout.addWidget(listing)
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
                "listing": listing
            },
            "label": {
                "message": message
            }
        }

        load_button.clicked.connect(self.on_load)
        stop_button.clicked.connect(self.on_stop)
        listing.currentItemChanged.connect(self.on_data_changed)

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

    def on_data_changed(self, *args):
        button = self.data["button"]["load"]
        item = self.data["model"]["listing"].currentItem()
        button.setEnabled(item.data(QtCore.Qt.ItemIsEnabled))

    def refresh(self):
        """Load assets from disk and add them to a QListView

        This method runs part-asynchronous, in that it blocks
        when busy, but takes brief intermissions between each
        asset found so as to lighten the load off of disk, and
        to enable the artist to abort searching once the target
        asset has been found.

        """

        listing = self.data["model"]["listing"]
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
            listing.addItem(item)

            lib.defer(25, on_next)

        def on_finished():
            state["running"] = False

            if not has["assets"]:
                item = QtWidgets.QListWidgetItem("No assets found")
                item.setData(QtCore.Qt.ItemIsEnabled, False)
                listing.addItem(item)

            listing.setCurrentItem(listing.item(0))
            listing.setFocus()
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

        listing = self.data["model"]["listing"]
        autoclose_checkbox = self.data["button"]["autoclose"]

        item = listing.currentItem()

        if item is not None:
            asset = item.data(AssetRole)
            assert asset

            try:
                api.registered_host().load(asset)

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
