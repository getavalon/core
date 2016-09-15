import sys
import contextlib

from ...vendor.Qt import QtWidgets, QtCore

import lib


self = sys.modules[__name__]
self._window = None


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Starter Instance Creator")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        lists = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        container = QtWidgets.QWidget()

        listing = QtWidgets.QListWidget()
        name = QtWidgets.QLineEdit()

        layout = QtWidgets.QVBoxLayout(container)
        layout.addWidget(QtWidgets.QLabel("Family"))
        layout.addWidget(listing)
        layout.addWidget(QtWidgets.QLabel("Name"))
        layout.addWidget(name)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)

        useselection_chk = QtWidgets.QCheckBox("Use selection")
        useselection_chk.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(useselection_chk, 0, 0)

        autoclose_chk = QtWidgets.QCheckBox("Close after creation")
        autoclose_chk.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(autoclose_chk, 1, 0)

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
            error_msg: "Error Message",
        }

        for widget, name_ in names.items():
            widget.setObjectName(name_)

        create_btn.clicked.connect(self.on_create)
        name.returnPressed.connect(self.on_create)
        name.textChanged.connect(self.on_data_changed)
        listing.currentItemChanged.connect(self.on_data_changed)

        # Defaults
        self.resize(220, 250)
        name.setFocus()
        create_btn.setEnabled(False)

    def on_data_changed(self, *args):
        button = self.findChild(QtWidgets.QPushButton, "Create Button")
        name = self.findChild(QtWidgets.QWidget, "Name")
        item = self.findChild(QtWidgets.QWidget, "Listing").currentItem()

        button.setEnabled(
            name.text().strip() != "" and
            item.data(QtCore.Qt.ItemIsEnabled)
        )

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands
        whilst trying to name an instance.

        """
        pass

    def refresh(self):
        listing = self.findChild(QtWidgets.QWidget, "Listing")

        if lib.families:
            for family in sorted(lib.families, key=lambda i: i["name"]):
                item = QtWidgets.QListWidgetItem(family["name"])
                item.setData(QtCore.Qt.ItemIsEnabled, True)
                item.setData(QtCore.Qt.UserRole + 2, family.get("help"))
                listing.addItem(item)

        else:
            item = QtWidgets.QListWidgetItem("No registered families")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            listing.addItem(item)

        listing.setCurrentItem(listing.item(0))

    def on_create(self):
        listing = self.findChild(QtWidgets.QWidget, "Listing")
        autoclose_chk = self.findChild(QtWidgets.QWidget,
                                       "Autoclose Checkbox")
        use_selection_chk = self.findChild(QtWidgets.QWidget,
                                           "Use Selection Checkbox")
        error_msg = self.findChild(QtWidgets.QWidget, "Error Message")

        item = listing.currentItem()

        if item is not None:
            family = item.text()
            name = self.findChild(QtWidgets.QWidget, "Name").text()
            use_selection = use_selection_chk.checkState()

            try:
                lib.create(name, family, use_selection)

            except NameError as e:
                error_msg.setText(str(e))
                error_msg.show()
                raise

            except (TypeError, RuntimeError, KeyError) as e:
                error_msg.setText("Program error: %s" % str(e))
                error_msg.show()
                raise

        if autoclose_chk.checkState():
            self.close()


def show():
    if self._window:
        self._window.close()
        del(self._window)

    try:
        widgets = QtWidgets.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets["MayaWindow"]
    except KeyError:
        parent = None

    window = Window(parent)
    window.show()
    window.refresh()

    self._window = window


@contextlib.contextmanager
def application():
    app = QtWidgets.QApplication(sys.argv)
    yield
    app.exec_()


if __name__ == '__main__':
    with application():
        show()
