import os
import sys

# from ...vendor import qtawesome
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

        # Store the widgets for lookup in here
        self.data = dict()

        body = QtWidgets.QWidget()
        lists = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        container = QtWidgets.QWidget()

        listing = QtWidgets.QListWidget()
        asset = QtWidgets.QLineEdit()
        name = QtWidgets.QLineEdit()
        result = QtWidgets.QLineEdit()
        result.setReadOnly(True)

        # region Menu for default subset names

        subset_button = QtWidgets.QPushButton()
        subset_button.setFixedWidth(18)
        subset_button.setFixedHeight(20)
        subset_menu = QtWidgets.QMenu(subset_button)
        subset_button.setMenu(subset_menu)

        # endregion

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(name)
        name_layout.addWidget(subset_button)
        name_layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(container)
        layout.addWidget(QtWidgets.QLabel("Family"))
        layout.addWidget(listing)
        layout.addWidget(QtWidgets.QLabel("Asset"))
        layout.addWidget(asset)
        layout.addWidget(QtWidgets.QLabel("Subset"))
        layout.addLayout(name_layout)
        layout.addWidget(result)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()

        useselection_chk = QtWidgets.QCheckBox("Use selection")
        useselection_chk.setCheckState(QtCore.Qt.Checked)

        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)
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

        self.data = {
            "Create Button": create_btn,
            "Listing": listing,
            "Use Selection Checkbox": useselection_chk,
            "Subset": name,
            "Subset Menu": subset_menu,
            "Result": result,
            "Asset": asset,
            "Error Message": error_msg,
        }

        for _name, widget in self.data.items():
            widget.setObjectName(_name)

        create_btn.clicked.connect(self.on_create)
        name.returnPressed.connect(self.on_create)
        name.textChanged.connect(self.on_data_changed)
        asset.textChanged.connect(self.on_data_changed)
        listing.currentItemChanged.connect(self.on_selection_changed)

        # Defaults
        self.resize(220, 300)
        name.setFocus()
        create_btn.setEnabled(False)

    def _build_menu(self, default_names):
        """Create optional predefines subset names

        Args:
            default_names(list): all predefined names

        Returns:
             None
        """

        menu = self.data["Subset Menu"]
        button = menu.parent()

        # Get and destroy the action group
        group = button.findChild(QtWidgets.QActionGroup)
        if group:
            group.deleteLater()

        state = any(default_names)
        button.setEnabled(state)
        if state is False:
            return

        # Build new action group
        group = QtWidgets.QActionGroup(button)
        for name in default_names:
            action = group.addAction(name)
            menu.addAction(action)

        group.triggered.connect(self._on_action_clicked)

    def _on_action_clicked(self, action):
        name = self.data["Subset"]
        name.setText(action.text())

    def _on_data_changed(self):

        listing = self.data["Listing"]
        asset_name = self.data["Asset"]
        subset = self.data["Subset"]
        result = self.data["Result"]
        button = self.data["Create Button"]

        item = listing.currentItem()
        subset_name = subset.text()
        asset_name = asset_name.text()

        # Get the assets from the database which match with the name
        assets_db = io.find(filter={"type": "asset"}, projection={"name": 1})
        assets = [asset for asset in assets_db if asset_name in asset["name"]]

        if assets:
            # Get all subsets of the current asset
            asset_ids = [asset["_id"] for asset in assets]
            subsets = io.find(filter={"type": "subset",
                                      "parent": {"$in": asset_ids}}) or []

            subsets = [subset["name"] for subset in subsets]
            self._build_menu(subsets)

            # Update the result
            plugin = item.data(PluginRole)
            family = plugin.family.rsplit(".", 1)[-1]
            if subset_name:
                subset_name = subset_name[0].upper() + subset_name[1:]
            result.setText("{}{}".format(family, subset_name))

            item.setData(ExistsRole, True)
            self.echo("Ready ..")
        else:
            self._build_menu([])
            item.setData(ExistsRole, False)
            self.echo("'%s' not found .." % asset_name)

        button.setEnabled(
            subset_name.strip() != "" and
            asset_name.strip() != "" and
            item.data(QtCore.Qt.ItemIsEnabled) and
            item.data(ExistsRole)
        )

    def on_data_changed(self, *args):
        button = self.data["Create Button"]
        button.setEnabled(False)
        lib.schedule(self._on_data_changed, 500, channel="gui")

    def on_selection_changed(self, *args):
        name = self.data["Subset"]
        item = self.data["Listing"].currentItem()

        plugin = item.data(PluginRole)
        if plugin is None:
            return

        label = "Default"
        name.setText(label)

        self.on_data_changed()

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands
        whilst trying to name an instance.

        """

    def refresh(self):

        listing = self.data["Listing"]
        asset = self.data["Asset"]
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

        asset = self.data["Asset"]
        listing = self.data["Listing"]
        result = self.data["Result"]

        item = listing.currentItem()
        useselection_chk = self.data["Use Selection Checkbox"]

        if item is not None:
            subset_name = result.text()
            asset = asset.text()
            family = item.data(FamilyRole)
        else:
            return

        try:
            host = api.registered_host()
            host.create(subset_name,
                        asset,
                        family,
                        options={"useSelection":
                                 useselection_chk.checkState()}
                        )

        except NameError as e:
            self.echo(e)
            raise

        except (TypeError, RuntimeError, KeyError, AssertionError) as e:
            self.echo("Program error: %s" % str(e))
            raise

    def echo(self, message):
        widget = self.data["Error Message"]
        widget.setText(str(message))
        widget.show()

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
