import itertools

from avalon.vendor.Qt import QtWidgets, QtCore, QtCompat


class Window(QtWidgets.QMainWindow):
    title = "Conventions"

    def __init__(self, model, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle(self.title)

        # Setup

        pages = {
            "home": QtWidgets.QWidget(),
        }

        panels = {
            "header": QtWidgets.QWidget(),
            "body": QtWidgets.QWidget(),
            "footer": QtWidgets.QWidget(),
            "sidebar": QtWidgets.QDockWidget(),
        }

        widgets = {
            "pages": QtWidgets.QStackedWidget(),

            "editMode": QtWidgets.QPushButton("Edit"),
            "guidelines": QtWidgets.QTableView(),
            "description": QtWidgets.QTextEdit(),
            "state": QtWidgets.QLabel("Ready"),

            "sidebar": QtWidgets.QWidget(),
        }

        for name, widget in itertools.chain(panels.items(),
                                            widgets.items(),
                                            pages.items()):
            # Expose to CSS
            widget.setObjectName(name)

            # Support for CSS
            widget.setAttribute(QtCore.Qt.WA_StyledBackground)

        # Initialisation

        self.setCentralWidget(widgets["pages"])
        widgets["pages"].addWidget(pages["home"])

        layout = QtWidgets.QVBoxLayout(panels["header"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["editMode"])

        layout = QtWidgets.QVBoxLayout(panels["body"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["guidelines"])

        layout = QtWidgets.QVBoxLayout(panels["footer"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["state"])

        layout = QtWidgets.QGridLayout(pages["home"])
        layout.addWidget(panels["header"], 0, 0)
        layout.addWidget(panels["body"], 1, 0)
        layout.addWidget(panels["footer"], 2, 0)

        layout = QtWidgets.QVBoxLayout(widgets["sidebar"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["description"])

        panels["sidebar"].setWidget(widgets["sidebar"])

        area = QtCore.Qt.RightDockWidgetArea
        self.addDockWidget(area, panels["sidebar"])

        widgets["editMode"].setCheckable(True)

        guidelines = widgets["guidelines"]
        guidelines.setShowGrid(False)
        guidelines.setModel(model)
        guidelines.verticalHeader().hide()

        guidelines.setVerticalScrollMode(QtWidgets.QTableView.ScrollPerPixel)
        guidelines.setHorizontalScrollMode(QtWidgets.QTableView.ScrollPerPixel)
        guidelines.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        guidelines.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        header = guidelines.horizontalHeader()
        QtCompat.setSectionResizeMode(header, 0, QtWidgets.QHeaderView.Stretch)

        # Signals

        selectionModel = guidelines.selectionModel()
        selectionModel.selectionChanged.connect(self.onGuidelineChanged)

        statusBar = self.statusBar()
        statusBar.showMessage("Booting..")

        self._pages = pages
        self._panels = panels
        self._widgets = widgets
        self._model = model

        # Post-initialisation

        selectionModel.select(
            model.createIndex(0, 0),
            selectionModel.ClearAndSelect
        )

        guidelines.setFocus()
        self.resize(700, 400)

    def onGuidelineChanged(self, selected, deselected):
        index = selected.indexes()[0]
        model = index.model()
        text = model.data(index, model.ContentRole)

        self._widgets["description"].setPlainText(text)
