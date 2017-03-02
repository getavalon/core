import os
import sys

from ...vendor.Qt import QtWidgets, QtCore
from .. import lib

self = sys.modules[__name__]
self._window = None

PathRole = QtCore.Qt.UserRole + 1


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Mindbender Launcher")

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        #  ___________________________________
        # |        |        |        |        |
        # |        |        |        |        |
        # |        |        |        |        |
        # |        |        |        |        |
        # |        |        |        |        |
        # |________|________|________|________|
        #
        projects = QtWidgets.QListWidget()
        assets = QtWidgets.QListWidget()
        tasks = QtWidgets.QListWidget()
        apps = QtWidgets.QListWidget()

        #  ________ ________
        # |        \        \
        # | assets |  shots |
        # |________|________|
        #
        silos = QtWidgets.QWidget()
        silo_assets = QtWidgets.QPushButton("Assets")
        silo_shots = QtWidgets.QPushButton("Shots")

        for silo in (silo_assets, silo_shots):
            silo.setCheckable(True)

        layout = QtWidgets.QHBoxLayout(silos)
        layout.addWidget(silo_assets)
        layout.addWidget(silo_shots)
        layout.setContentsMargins(0, 0, 0, 0)

        assets_container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(assets_container)
        layout.addWidget(silos)
        layout.addWidget(assets)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(projects)
        layout.addWidget(assets_container)
        layout.addWidget(tasks)
        layout.addWidget(apps)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()

        closeonload_chk = QtWidgets.QCheckBox()
        closeonload_lbl = QtWidgets.QLabel("Close on load")
        closeonload_chk.setCheckState(QtCore.Qt.Checked)
        layout = QtWidgets.QGridLayout(options)
        layout.addWidget(closeonload_chk, 0, 0)
        layout.addWidget(closeonload_lbl, 0, 1)
        layout.setContentsMargins(0, 0, 0, 0)

        btn_load = QtWidgets.QPushButton("Load")
        btn_load.setFixedWidth(80)
        btn_refresh = QtWidgets.QPushButton("Refresh")
        btn_refresh.setFixedWidth(80)

        layout = QtWidgets.QHBoxLayout(footer)
        layout.addWidget(btn_refresh)
        layout.addWidget(btn_load)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(options, 0, QtCore.Qt.AlignRight)
        layout.addWidget(footer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.data = {
            "state": {
                "root": None,
            },
            "views": {
                "1": projects,
                "2": assets,
                "3": tasks,
                "4": apps,
            },
            "buttons": {
                "load": btn_load,
                "refresh": btn_refresh,
                "autoclose": closeonload_chk,
            },
            "silos": {
                "assets": silo_assets,
                "shots": silo_shots,
            }
        }

        btn_load.clicked.connect(self.on_launch_clicked)
        btn_refresh.clicked.connect(self.on_refresh_clicked)

        silo_assets.checked.connect(self.on_assets_checked)
        silo_shots.checked.connect(self.on_shots_checked)

        projects.currentItemChanged.connect(self.on_project_changed)
        assets.currentItemChanged.connect(self.on_2_changed)
        tasks.currentItemChanged.connect(self.on_3_changed)
        apps.currentItemChanged.connect(self.on_4_changed)

        self.resize(600, 250)

    def on_launch_clicked(self):
        # item = self.data["views"]["4"].currentItem()
        # root = item.data(QtCore.Qt.UserRole + 1)
        # lib.load(root)

        if self.data["buttons"]["autoclose"].checkState():
            self.close()

    def on_refresh_clicked(self):
        self.refresh(root=self.data["root"])

    def on_shots_checked(self):
        pass

    def on_assets_checked(self):
        pass

    def refresh(self, root):
        for view in self.data["views"].values():
            view.clear()

        self.data["root"] = root
        self.data["buttons"]["load"].setEnabled(False)

        view = self.data["views"]["1"]
        for path in walk(root):
            item = QtWidgets.QListWidgetItem(os.path.basename(path))
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(PathRole, path)
            view.addItem(item)

        view.setCurrentItem(view.item(0))

    def on_project_changed(self, current, previous):
        """List items of asset"""
        views = self.data["views"]
        views["2"].clear()

        if not views["1"].currentItem():
            return

        if not views["1"].currentItem().data(QtCore.Qt.ItemIsEnabled):
            return

        root = current.data(PathRole)

        if self.data["silos"]["assets"].isChecked():
            pass

        no_items = True
        for path in walk(root):
            item = QtWidgets.QListWidgetItem(os.path.basename(path))
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(PathRole, path)
            views["2"].addItem(item)
            no_items = False

        if no_items:
            item = QtWidgets.QListWidgetItem("No items")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            views["2"].addItem(item)

    def on_2_changed(self, current, previous):
        """List items of asset"""
        self.data["buttons"]["load"].setEnabled(False)
        self.data["views"]["3"].clear()

        if not self.data["views"]["2"].currentItem():
            return

        if self.data["views"]["2"].currentItem().text() == "No items":
            return

        root = current.data(PathRole)
        root = os.path.join(root, "publish")

        no_items = True
        for path in walk(root):
            item = QtWidgets.QListWidgetItem(os.path.basename(path))
            item.setData(PathRole, path)
            self.data["views"]["3"].addItem(item)
            no_items = False

        if no_items:
            item = QtWidgets.QListWidgetItem("No items")
            self.data["views"]["3"].addItem(item)

    def on_3_changed(self, current, previous):
        self.data["buttons"]["load"].setEnabled(False)
        self.data["views"]["4"].clear()

        if not self.data["views"]["3"].currentItem():
            return

        if self.data["views"]["3"].currentItem().text() == "No items":
            return

        root = current.data(PathRole)

        no_items = True
        for i in walk(root):
            item = QtWidgets.QListWidgetItem(os.path.basename(i))
            item.setData(PathRole, i)
            self.data["views"]["4"].addItem(item)
            no_items = False

        if no_items:
            item = QtWidgets.QListWidgetItem("No items")
            self.data["views"]["4"].addItem(item)

    def on_4_changed(self, current, previous):
        if not self.data["views"]["4"].currentItem():
            return

        if self.data["views"]["4"].currentItem().text() == "No items":
            return

        # root = current.data(PathRole)


def show(debug=False):
    """Display Launcher GUI

    Arguments:
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    if self._window:
        self._window.close()
        del(self._window)

    root = os.getcwd()

    with lib.application():
        window = Window()
        window.show()
        window.refresh(root)

        self._window = window


def walk(root):
    try:
        base, dirs, files = next(os.walk(root))
    except OSError as e:
        # Ignore non-existing dirs
        print(e)
        return

    for dirname in dirs:
        yield os.path.join(root, dirname)
