import os
import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import pipeline
from .. import lib

self = sys.modules[__name__]
self._window = None

HelpRole = QtCore.Qt.UserRole + 2
FamilyRole = QtCore.Qt.UserRole + 3


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Instance Creator")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        lists = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        container = QtWidgets.QWidget()

        listing = QtWidgets.QListWidget()
        asset = QtWidgets.QLineEdit()
        name = QtWidgets.QLineEdit()

        layout = QtWidgets.QVBoxLayout(container)
        layout.addWidget(QtWidgets.QLabel("Family"))
        layout.addWidget(listing)
        layout.addWidget(QtWidgets.QLabel("Asset"))
        layout.addWidget(asset)
        layout.addWidget(QtWidgets.QLabel("Subset"))
        layout.addWidget(name)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()

        autoclose_chk = QtWidgets.QCheckBox("Auto-close")
        autoclose_chk.setCheckState(QtCore.Qt.Checked)
        useselection_chk = QtWidgets.QCheckBox("Use selection")
        useselection_chk.setCheckState(QtCore.Qt.Checked)

        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(autoclose_chk, 1, 0)
        layout.addWidget(useselection_chk, 1, 1)

        layout = QtWidgets.QHBoxLayout(lists)
        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(body)
        layout.addWidget(lists)
        layout.addWidget(options, 0, QtCore.Qt.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)

        create_btn = QtWidgets.QPushButton("Create")
        error_msg = QtWidgets.QLabel()
        error_msg.hide()

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(create_btn)
        layout.addWidget(error_msg)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        names = {
            create_btn: "Create Button",
            listing: "Listing",
            useselection_chk: "Use Selection Checkbox",
            autoclose_chk: "Autoclose Checkbox",
            name: "Name",
            asset: "Asset",
            error_msg: "Error Message",
        }

        for widget, name_ in names.items():
            widget.setObjectName(name_)

        create_btn.clicked.connect(self.on_create)
        name.returnPressed.connect(self.on_create)
        name.textChanged.connect(self.on_name_changed)
        asset.textChanged.connect(self.on_asset_changed)
        listing.currentItemChanged.connect(self.on_selection_changed)

        # Defaults
        self.resize(220, 250)
        name.setFocus()
        create_btn.setEnabled(False)

    def on_asset_changed(self, *args):
        button = self.findChild(QtWidgets.QPushButton, "Create Button")
        asset = self.findChild(QtWidgets.QWidget, "Asset")
        name = self.findChild(QtWidgets.QWidget, "Name")
        item = self.findChild(QtWidgets.QWidget, "Listing").currentItem()

        button.setEnabled(
            name.text().strip() != "" and
            asset.text().strip() != "" and
            item.data(QtCore.Qt.ItemIsEnabled)
        )

    def on_name_changed(self, *args):
        button = self.findChild(QtWidgets.QPushButton, "Create Button")
        asset = self.findChild(QtWidgets.QWidget, "Asset")
        name = self.findChild(QtWidgets.QWidget, "Name")
        item = self.findChild(QtWidgets.QWidget, "Listing").currentItem()

        button.setEnabled(
            name.text().strip() != "" and
            asset.text().strip() != "" and
            item.data(QtCore.Qt.ItemIsEnabled)
        )

    def on_selection_changed(self, *args):
        button = self.findChild(QtWidgets.QPushButton, "Create Button")
        name = self.findChild(QtWidgets.QWidget, "Name")
        item = self.findChild(QtWidgets.QWidget, "Listing").currentItem()

        button.setEnabled(
            name.text().strip() != "" and
            item.data(QtCore.Qt.ItemIsEnabled)
        )

        # Set default name, e.g. modelDefault, lookdevDefault
        label = item.data(FamilyRole) or "null"
        label = label.rsplit(".")[-1]
        label = label.lower() + "Default"

        name.setText(label)

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands
        whilst trying to name an instance.

        """

    def refresh(self, families):
        listing = self.findChild(QtWidgets.QWidget, "Listing")
        asset = self.findChild(QtWidgets.QWidget, "Asset")
        asset.setText(os.environ["MINDBENDER_ASSET"])

        has_families = False

        for family in sorted(families.values(), key=lambda f: f["name"]):
            item = QtWidgets.QListWidgetItem(family["label"] or family["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(HelpRole, family["help"])
            item.setData(FamilyRole, family["name"])
            listing.addItem(item)

            has_families = True

        if not has_families:
            item = QtWidgets.QListWidgetItem("No registered families")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            listing.addItem(item)

        listing.setCurrentItem(listing.item(0))

    def on_create(self):
        asset = self.findChild(QtWidgets.QWidget, "Asset")
        listing = self.findChild(QtWidgets.QWidget, "Listing")
        autoclose_chk = self.findChild(QtWidgets.QWidget,
                                       "Autoclose Checkbox")
        useselection_chk = self.findChild(QtWidgets.QWidget,
                                          "Use Selection Checkbox")
        error_msg = self.findChild(QtWidgets.QWidget, "Error Message")

        asset = asset.text()
        item = listing.currentItem()

        if item is not None:
            family = item.data(FamilyRole)
            name = self.findChild(QtWidgets.QWidget, "Name").text()

            try:
                host = pipeline.registered_host()
                host.create(asset, name, family, options={
                    "useSelection": bool(useselection_chk.checkState())
                })

            except NameError as e:
                error_msg.setText(str(e))
                error_msg.show()
                raise

            except (TypeError, RuntimeError, KeyError, AssertionError) as e:
                error_msg.setText("Program error: %s" % str(e))
                error_msg.show()
                raise

        if autoclose_chk.checkState():
            self.close()


def show(debug=False, parent=None):
    """Display asset creator GUI

    Arguments:
        creator (func, optional): Callable function, passed `name`,
            `family` and `use_selection`, defaults to `creator`
            defined in :mod:`pipeline`
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    families = pipeline.registered_families()

    if self._window:
        self._window.close()
        del(self._window)

    if debug:
        pipeline.register_family("debug.model")
        pipeline.register_family("debug.rig")
        pipeline.register_family("debug.animation")

    with lib.application():
        window = Window(parent)
        window.refresh(families)
        window.show()

        self._window = window
