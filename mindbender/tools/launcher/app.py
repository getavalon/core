import os
import sys
import time
import getpass
import threading

from mindbender import api
from ...vendor.Qt import QtWidgets, QtCore
from ...vendor.six.moves import queue
from .. import lib

self = sys.modules[__name__]
self._window = None

LabelRole = QtCore.Qt.UserRole + 1
PathRole = QtCore.Qt.UserRole + 2
ObjectRole = QtCore.Qt.UserRole + 3


class _Window(QtWidgets.QDialog):

    _process_launched = QtCore.pyqtSignal(object)
    _process_wrote = QtCore.pyqtSignal(QtWidgets.QWidget, object)

    def __init__(self, parent=None):
        super(_Window, self).__init__(parent)
        self.setWindowTitle("Mindbender Launcher")

        tabs = QtWidgets.QTabBar()
        tabs.addTab("Browser")
        tabs.addTab("Monitor")

        page_browser = QtWidgets.QWidget()
        page_monitor = QtWidgets.QWidget()

        # Browser
        #
        #
        #
        #
        #
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

        #  _______ ________
        # |       \        \
        # | assets |  shots |
        # |________|________|
        #
        silos = QtWidgets.QTabBar()
        silos.addTab("Assets")
        silos.addTab("Film")

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

        spacer = QtWidgets.QWidget()
        btn_launch = QtWidgets.QPushButton("Load")
        btn_refresh = QtWidgets.QPushButton("Refresh")

        layout = QtWidgets.QHBoxLayout(footer)
        layout.addWidget(spacer, 1)  # Compress buttons to the right
        layout.addWidget(btn_refresh)
        layout.addWidget(btn_launch)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(page_browser)
        layout.addWidget(body)
        layout.addWidget(footer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        names = {
            body: "BrowserBody",
            footer: "BrowserFooter"
        }

        # Monitor
        #
        #
        #
        #
        #
        body = QtWidgets.QWidget()

        processes = QtWidgets.QListWidget()
        processes.setFixedWidth(150)
        process_placeholder = QtWidgets.QLabel("No process.")

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(processes)
        layout.addWidget(process_placeholder)

        layout = QtWidgets.QHBoxLayout(page_monitor)
        layout.addWidget(body)
        layout.setContentsMargins(0, 0, 0, 0)

        # Composition
        #
        #
        #
        #
        #
        pages = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(pages)
        layout.addWidget(tabs)
        layout.addWidget(page_browser)
        layout.addWidget(page_monitor)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(pages)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        names.update({
            body: "TerminalBody",
            processes: "TerminalProcesses",
            page_browser: "BrowserPage",
            page_monitor: "TerminalPage",
        })

        for widget, name in names.items():
            widget.setObjectName(name)

        self.data = {
            "state": {
                "root": None,
            },

            "pages": {
                "browser": page_browser,
                "monitor": page_monitor
            },

            "views": {
                "projects": projects,
                "assets": assets,
                "tasks": tasks,
                "apps": apps,
                "processes": processes,
            },
            "buttons": {
                "launch": btn_launch,
                "refresh": btn_refresh,
            },

            "tabs": tabs,
            "silos": silos,

            # Monitor newly launched processes
            "recentlyLaunched": queue.Queue(),

            # Reference to each running subprocess
            "runningApps": {
                "0": {
                    "widget": process_placeholder,
                }
            }
        }

        btn_launch.clicked.connect(self.on_launch_clicked)
        btn_refresh.clicked.connect(self.on_refresh_clicked)

        tabs.currentChanged.connect(self.on_tab_changed)
        silos.currentChanged.connect(self.on_silo_changed)

        projects.currentItemChanged.connect(self.on_project_changed)
        assets.currentItemChanged.connect(self.on_asset_changed)
        tasks.currentItemChanged.connect(self.on_task_changed)
        apps.currentItemChanged.connect(self.on_app_changed)
        processes.currentItemChanged.connect(self.on_process_changed)

        # Threaded communication
        self._process_launched.connect(self.on_process_launched)
        self._process_wrote.connect(self.on_process_wrote)

        self.resize(700, 350)
        self.monitor_launches()
        self.update_processes()

        # Defaults
        page_monitor.hide()

    def on_process_launched(self, process):
        # Wait 2 seconds before enabling user to launch another app.
        button = self.data["buttons"]["launch"]
        button.setEnabled(False)
        QtCore.QTimer.singleShot(2000, lambda: button.setEnabled(True))

        self.monitor_process(process)

    def on_process_wrote(self, widget, line):
        widget.append(line)
        sys.stdout.write("process: %s" % line)

    def monitor_launches(self):
        """Keep an eye on newly launched applications"""
        def _monitor():
            while True:
                process = self.data["recentlyLaunched"].get()
                self._process_launched.emit(process)
                print("'%s' launched.." % process["app"]["executable"])

        thread = threading.Thread(target=_monitor)
        thread.daemon = True
        thread.start()

    def monitor_launched(self):
        """Keep an eye on already launched applications"""

        def _purge():
            for process in self.data["runningApps"].values():
                if process["instance"].poll() is not None:
                    pass  # remove from list

        def _monitor():
            while True:
                time.sleep(1)
                _purge()

        thread = threading.Thread(target=_monitor)
        thread.daemon = True
        thread.start()

    def monitor_process(self, process):
        """Keep an eye on output from launched application"""
        def _monitor(widget):
            print("Monitoring %s.." % process["instance"])
            for line in api.stream(process["instance"].stdout):
                self._process_wrote.emit(widget, line)

        widget = QtWidgets.QTextEdit()
        widget.append("Running '%s'.." % process["app"]["executable"])
        widget.setStyleSheet("""
            QTextEdit {
                background: black;
                color: white;
            }
        """)

        body = self.findChild(QtWidgets.QWidget, "TerminalBody")
        body.layout().addWidget(widget)

        thread = threading.Thread(target=_monitor, args=[widget])
        thread.daemon = True
        thread.start()

        time = api.time()
        process.update({
            "thread": thread,
            "widget": widget,
            "time": time
        })

        for app in self.data["runningApps"].values():
            app["widget"].hide()

        self.data["runningApps"][time] = process
        self.update_processes()

        return thread

    def on_tab_changed(self, index):
        if self.data["tabs"].tabText(index) == "Browser":
            self.data["pages"]["browser"].show()
            self.data["pages"]["monitor"].hide()
        else:
            self.data["pages"]["browser"].hide()
            self.data["pages"]["monitor"].show()

    def on_launch_clicked(self):
        views = self.data["views"]
        project = views["projects"].currentItem().data(LabelRole)
        asset = views["assets"].currentItem().data(LabelRole)
        task = views["tasks"].currentItem().data(LabelRole)
        app = views["apps"].currentItem().data(ObjectRole)
        user = getpass.getuser()

        print(
            "Launching {app} as '{user}' doing '{task}' "
            "@ '{project}/{asset}'..".format(app=app["executable"],
                                             user=user.title(),
                                             task=task,
                                             project=project,
                                             asset=asset)
        )

        self.launch(app)

    def on_refresh_clicked(self):
        self.refresh(root=self.data["root"])

    def refresh(self, root):
        for view in self.data["views"].values():
            view.clear()

        self.data["root"] = root
        self.data["buttons"]["launch"].setEnabled(False)

        view = self.data["views"]["projects"]
        for path in walk(root):
            label = os.path.basename(path)
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(PathRole, path)
            item.setData(LabelRole, label)
            view.addItem(item)

        view.setCurrentItem(view.item(0))

    def on_process_changed(self, current, previous):
        if not current:
            return

        if not current.data(QtCore.Qt.ItemIsEnabled):
            return

        for app in self.data["runningApps"].values():
            app["widget"].hide()

        process = current.data(ObjectRole)
        process["widget"].show()

    def update_processes(self):
        view = self.data["views"]["processes"]
        view.clear()

        for process in self.data["runningApps"].values():

            # Placeholder process have no app
            if "app" not in process:
                continue

            label = process["app"].get(
                "label", os.path.basename(process["app"]["executable"])
            )

            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(ObjectRole, process)
            view.addItem(item)

    def on_project_changed(self, current, previous):
        """User changed project"""
        if not current:
            return

        if not current.data(QtCore.Qt.ItemIsEnabled):
            return

        root = current.data(PathRole)
        QtCore.QTimer.singleShot(
            100,
            lambda: self.update_assets(project=root)
        )

    def on_silo_changed(self, index):
        """User changed silo"""
        projects = self.data["views"]["projects"]

        tasks = self.data["views"]["assets"]
        tasks.clear()

        root = projects.currentItem().data(PathRole)
        QtCore.QTimer.singleShot(
            100,
            lambda: self.update_assets(project=root)
        )

    def on_asset_changed(self, current, previous):
        """User changed asset"""
        self.data["buttons"]["launch"].setEnabled(False)
        self.data["views"]["tasks"].clear()

        if not current:
            return

        if not current.data(QtCore.Qt.ItemIsEnabled):
            return

        root = current.data(PathRole)
        QtCore.QTimer.singleShot(
            100,
            lambda: self.update_tasks(asset=root)
        )

    def on_task_changed(self, current, previous):
        """User changed task"""
        self.data["buttons"]["launch"].setEnabled(False)
        self.data["views"]["apps"].clear()

        if not current:
            return

        if not current.data(QtCore.Qt.ItemIsEnabled):
            return

        root = current.data(PathRole)
        self.update_apps(root)

    def on_app_changed(self, current, previous):
        if not current:
            return

        if not current.data(QtCore.Qt.ItemIsEnabled):
            return

        self.data["buttons"]["launch"].setEnabled(True)

    def launch(self, app):
        try:
            print("app: Launching %s" % app["executable"])
            popen = api.launch(
                executable=app["executable"],
                args=app.get("args", [])
            )
        except ValueError as e:
            print(e)
            return

        except OSError as e:
            print(e)
            return

        self.data["recentlyLaunched"].put({
            "instance": popen,
            "app": app
        })

    def update_assets(self, project):
        views = self.data["views"]
        silos = self.data["silos"]
        silo = silos.tabText(silos.currentIndex())
        root = os.path.join(project, silo)

        no_items = True
        for path in walk(root):
            label = os.path.basename(path)
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(PathRole, path)
            item.setData(LabelRole, label)
            views["assets"].addItem(item)
            no_items = False

        if no_items:
            item = QtWidgets.QListWidgetItem("No tasks")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            views["assets"].addItem(item)

    def update_tasks(self, asset):
        root = os.path.join(asset, "work")

        no_items = True
        for path in walk(root):
            label = os.path.basename(path)
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(PathRole, path)
            item.setData(LabelRole, label)
            self.data["views"]["tasks"].addItem(item)
            no_items = False

        if no_items:
            item = QtWidgets.QListWidgetItem("No items")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            self.data["views"]["tasks"].addItem(item)

    def update_apps(self, task):
        view = self.data["views"]["apps"]

        no_items = True
        for executable, app in api.registered_apps().items():
            label = app.get("label", executable)
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(ObjectRole, app)
            item.setData(LabelRole, label)
            view.addItem(item)
            no_items = False

        if no_items:
            item = QtWidgets.QListWidgetItem("No apps")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            self.data["views"]["apps"].addItem(item)


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

    if debug:
        api.register_app({
            "executable": "python",
            "label": "Print",
            "args": ["-u", "-c", "print('Something nice')"]
        })
        api.register_app({
            "executable": "notepad",
            "label": "Notepad"
        })
        api.register_app({
            "executable": "maya2016",
            "args": ["-hideConsole"],
            "label": "Maya"
        })
        api.register_app({
            "executable": "nuke10",
            "label": "Nuke"
        })

    with lib.application():
        window = _Window()
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
