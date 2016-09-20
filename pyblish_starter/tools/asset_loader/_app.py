import sys

from ... import _pipeline, ls
from ...vendor.Qt import QtWidgets, QtCore
from .. import _lib


self = sys.modules[__name__]
self._window = None


class Window(QtWidgets.QDialog):
    def __init__(self, loader, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Asset Loader")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.loader = loader

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
        error_msg = QtWidgets.QLabel()
        error_msg.hide()

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(load_button)
        layout.addWidget(error_msg)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.data = {
            "button": {
                "load": load_button,
                "autoclose": autoclose_checkbox,
            },
            "model": {
                "listing": listing
            },
            "label": {
                "error": error_msg
            }
        }

        load_button.clicked.connect(self.on_load)
        listing.currentItemChanged.connect(self.on_data_changed)

        # Defaults
        self.resize(220, 250)
        load_button.setFocus()
        load_button.setEnabled(False)

    def on_data_changed(self, *args):
        button = self.data["button"]["load"]
        item = self.data["model"]["listing"].currentItem()
        button.setEnabled(item.data(QtCore.Qt.ItemIsEnabled))

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands
        whilst trying to name an instance.

        """

    def refresh(self, root):
        listing = self.data["model"]["listing"]

        try:
            assets = ls(root)
        except OSError:
            assets = list()

        if assets:
            for asset in assets:
                item = QtWidgets.QListWidgetItem(asset)
                item.setData(QtCore.Qt.ItemIsEnabled, True)
                listing.addItem(item)

        else:
            item = QtWidgets.QListWidgetItem("No assets found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            listing.addItem(item)

        listing.setCurrentItem(listing.item(0))

    def on_load(self):
        listing = self.data["model"]["listing"]
        autoclose_checkbox = self.data["button"]["autoclose"]
        error_msg = self.data["label"]["error"]

        item = listing.currentItem()

        if item is not None:
            try:
                self.loader(item.text())

            except NameError as e:
                error_msg.setText(str(e))
                error_msg.show()
                raise

            except (TypeError, RuntimeError, KeyError) as e:
                error_msg.setText("Program error: %s" % str(e))
                error_msg.show()
                raise

        if autoclose_checkbox.checkState():
            self.close()


def show(root, loader, debug=False):
    """Display Asset Loader GUI

    Arguments:
        root (str): Absolute path to root directory of assets
        loader (func): Callable function, passed `name` of asset.
        debug (bool): Run loader in debug-mode

    """

    if self._window:
        self._window.close()
        del(self._window)

    loader = loader or _pipeline._loader

    if loader is None:
        raise ValueError("No loader registered.\n"
                         "A loader must be either registered in "
                         "pyblish_starter.setup(loader=) or "
                         "passed to show(loader=).")

    try:
        widgets = QtWidgets.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets["MayaWindow"]
    except KeyError:
        parent = None

    with _lib.application():
        window = Window(loader, parent)
        window.show()
        window.refresh(root)

        self._window = window


if __name__ == '__main__':
    import os

    show(root=os.path.expanduser("~"),
         loader=lambda name: None)
