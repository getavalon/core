import os
import sys

from ...vendor.Qt import QtWidgets, QtCore
from ... import api, io
from .. import lib

module = sys.modules[__name__]
module.window = None
module.root = api.registered_root()

HelpRole = QtCore.Qt.UserRole + 2
FamilyRole = QtCore.Qt.UserRole + 3
ExistsRole = QtCore.Qt.UserRole + 4
PluginRole = QtCore.Qt.UserRole + 5


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
        error_msg.setFixedHeight(20)

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
            name: "Subset",
            asset: "Asset",
            error_msg: "Error Message",
        }

        for widget, name_ in names.items():
            widget.setObjectName(name_)

        create_btn.clicked.connect(self.on_create)
        name.returnPressed.connect(self.on_create)
        asset.textChanged.connect(self.on_data_changed)
        name.textChanged.connect(self.on_data_changed)
        listing.currentItemChanged.connect(self.on_selection_changed)

        # Defaults
        self.resize(220, 250)
        name.setFocus()
        create_btn.setEnabled(False)

    def on_data_changed(self, *args):
        button = self.findChild(QtWidgets.QPushButton, "Create Button")
        button.setEnabled(False)
        lib.schedule(self._on_data_changed, 500, channel="gui")

    def on_selection_changed(self, *args):
        name = self.findChild(QtWidgets.QWidget, "Subset")
        item = self.findChild(QtWidgets.QWidget, "Listing").currentItem()

        plugin = item.data(PluginRole)

        if plugin is None:
            return

        label = (
            plugin.name or
            plugin.family.lower().rsplit(".", 1)[-1] + "Default"
        )

        name.setText(label)

        self.on_data_changed()

    def _on_data_changed(self):
        button = self.findChild(QtWidgets.QPushButton, "Create Button")
        asset = self.findChild(QtWidgets.QWidget, "Asset")
        name = self.findChild(QtWidgets.QWidget, "Subset")
        item = self.findChild(QtWidgets.QWidget, "Listing").currentItem()

        if asset.text() in (asset["name"]
                            for asset in io.find(
                                filter={"type": "asset"},
                                projection={"name": 1})):
            item.setData(ExistsRole, True)
            self.echo("Ready..")

        else:
            item.setData(ExistsRole, False)
            self.echo("'%s' not found.." % asset.text())

        button.setEnabled(
            name.text().strip() != "" and
            asset.text().strip() != "" and
            item.data(QtCore.Qt.ItemIsEnabled) and
            item.data(ExistsRole)
        )

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands
        whilst trying to name an instance.

        """

    def refresh(self):
        listing = self.findChild(QtWidgets.QWidget, "Listing")
        asset = self.findChild(QtWidgets.QWidget, "Asset")
        asset.setText(os.environ["AVALON_ASSET"])

        has_families = False

        creators = api.discover(api.Creator)

        for creator in creators:
            label = creator.label or creator.family
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(HelpRole, creator.__doc__)
            item.setData(FamilyRole, creator.family)
            item.setData(PluginRole, creator)
            item.setData(ExistsRole, False)
            listing.addItem(item)

            has_families = True

        if not has_families:
            item = QtWidgets.QListWidgetItem("No registered families")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            listing.addItem(item)

        listing.setCurrentItem(listing.item(0))

    def on_create(self):
        button = self.findChild(QtWidgets.QPushButton, "Create Button")

        if not button.isEnabled():
            return

        asset = self.findChild(QtWidgets.QWidget, "Asset")
        listing = self.findChild(QtWidgets.QWidget, "Listing")
        autoclose_chk = self.findChild(QtWidgets.QWidget,
                                       "Autoclose Checkbox")
        useselection_chk = self.findChild(QtWidgets.QWidget,
                                          "Use Selection Checkbox")

        item = listing.currentItem()

        if item is not None:
            name = self.findChild(QtWidgets.QWidget, "Subset").text()
            asset = asset.text()
            family = item.data(FamilyRole)

            try:
                host = api.registered_host()
                host.create(name, asset, family, options={
                    "useSelection": useselection_chk.checkState()
                })

            except NameError as e:
                self.echo(e)
                raise

            except (TypeError, RuntimeError, KeyError, AssertionError) as e:
                self.echo("Program error: %s" % str(e))
                raise

        if autoclose_chk.checkState():
            self.close()

    def echo(self, message):
        widget = self.findChild(QtWidgets.QWidget, "Error Message")
        widget.setText(str(message))
        widget.show()
        print(message)

        lib.schedule(lambda: widget.setText(""), 5000, channel="message")


def show(debug=False, parent=None):
    """Display asset creator GUI

    Arguments:
        creator (func, optional): Callable function, passed `name`,
            `family` and `use_selection`, defaults to `creator`
            defined in :mod:`pipeline`
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    if module.window:
        module.window.close()
        del(module.window)

    if debug:
        from avalon import mock
        for creator in mock.creators:
            api.register_plugin(api.Creator, creator)

        import traceback
        sys.excepthook = lambda typ, val, tb: traceback.print_last()

        io.install()

        any_project = next(
            project for project in io.projects()
            if project.get("active", True) is not False
        )

        api.Session["AVALON_PROJECT"] = any_project["name"]
        module.project = any_project["name"]

    with lib.application():
        window = Window(parent)
        window.refresh()
        window.show()

        module.window = window
