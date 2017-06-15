import os
import sys
import time
import datetime

from ..projectmanager.widget import AssetWidget, AssetModel
from ...vendor.Qt import QtWidgets, QtCore, QtGui
from ... import api, io
from .. import lib
from .widgets import SubsetWidget

module = sys.modules[__name__]
module.window = None
module.root = api.registered_root()
module.project = os.getenv("MINDBENDER_PROJECT")
module.debug = bool(os.getenv("MINDBENDER_DEBUG"))

# Custom roles
DocumentRole = AssetModel.DocumentRole
RepresentationsRole = QtCore.Qt.UserRole + 2
LatestRole = QtCore.Qt.UserRole + 3
LocationRole = QtCore.Qt.UserRole + 4


class Window(QtWidgets.QDialog):
    """Asset loader interface"""

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle(
            "Asset Loader 2.0 - %s/%s" % (
                module.root, module.project))

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()
        footer.setFixedHeight(20)

        container = QtWidgets.QWidget()

        assets = AssetWidget()
        subsets = SubsetWidget()

        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        split = QtWidgets.QSplitter()
        split.addWidget(assets)
        split.addWidget(subsets)
        split.setStretchFactor(0, 30)
        split.setStretchFactor(1, 90)
        layout.addWidget(split)

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)

        message = QtWidgets.QLabel()
        message.hide()

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(message)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.data = {
            "model": {
                "assets": assets,
                "subsets": subsets,
                #"versions": versions,
                #"representations": representations,
            },
            "label": {
                "message": message,
            },
            "state": {
                "template": None,
                "locations": list(),
                "context": {
                    "root": None,
                    "project": None,
                    "asset": None,
                    "silo": None,
                    "subset": None,
                    "version": None,
                    "representation": None,
                },
            }
        }

        assets.selection_changed.connect(self.on_assetschanged)
        selection_model = subsets.view.selectionModel()
        #selection_model.selectionChanged.connect(self.on_subsetschanged)

        # Defaults
        self.resize(1100, 600)

    def on_copy_source_to_clipboard(self):
        source = self.data["label"]["source"].text()
        source = source.format(root=api.registered_root())
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(source)

    def on_copy_source_menu(self, pos):
        pos = QtGui.QCursor.pos()
        menu = QtWidgets.QMenu()
        action = menu.addAction("Copy to clipboard")
        action.triggered.connect(self.on_copy_source_to_clipboard)
        menu.move(pos)
        menu.exec_()

    def keyPressEvent(self, event):
        """Delegate keyboard events"""

        if event.key() == QtCore.Qt.Key_Return:
            return self.on_enter()

    def on_enter(self):
        self.on_load_pressed()

    # -------------------------------
    # Delay calling blocking methods
    # -------------------------------

    def refresh(self):
        self.echo("Fetching results..")
        lib.schedule(self._refresh, 100, channel="mongo")

    def on_assetschanged(self, *args):
        self.echo("Fetching results..")
        lib.schedule(self._assetschanged, 100, channel="mongo")

    def on_versionschanged(self, *args):
        self.echo("Fetching results..")
        lib.schedule(self._versionschanged, 100, channel="mongo")

    def on_representationschanged(self, *args):
        lib.schedule(self._representationschanged, 100, channel="mongo")

    # ------------------------------

    def _refresh(self):
        """Load assets from database"""

        project = io.find_one({"type": "project"})
        assert project, "This is a bug"

        assets_model = self.data["model"]["assets"]
        assets_model.refresh()
        assets_model.setFocus()

        # Update state
        state = self.data["state"]
        state["template"] = project["config"]["template"]["publish"]
        state["context"]["root"] = api.registered_root()
        state["context"]["project"] = project["name"]

    def _assetschanged(self):
        """Selected assets have changed"""

        assets_model = self.data["model"]["assets"]
        subsets_model = self.data["model"]["subsets"].model
        subsets_model.clear()

        t1 = time.time()

        asset_item = assets_model.get_active_index()
        if asset_item is None or not asset_item.isValid():
            return

        document = asset_item.data(DocumentRole)
        subsets_model.set_asset(document['_id'])

        self.data["state"]["context"]["asset"] = document["name"]
        self.data["state"]["context"]["silo"] = document["silo"]
        self.echo("Duration: %.3fs" % (time.time() - t1))

    def _versionschanged(self):
        self.data["label"]["commentContainer"].hide()
        self.data["label"]["createdContainer"].hide()
        self.data["label"]["sourceContainer"].hide()
        versions_model = self.data["model"]["versions"]
        representations_model = self.data["model"]["representations"]
        representations_model.clear()

        version_item = versions_model.currentItem()

        # Nothing is selected
        if version_item is None:
            return

        if not version_item.data(QtCore.Qt.ItemIsEnabled):
            return

        representations_by_name = {}

        t1 = time.time()

        if version_item.data(LatestRole):
            # Determine the latest version for each currently selected subset.

            subsets = self.data["model"]["subsets"].selectedItems()
            subsets = list(item.data(DocumentRole) for item in subsets)

            all_versions = io.find({
                "type": "version",
                "parent": {"$in": [subset["_id"] for subset in subsets]}
            })

            # What is the latest version per subset?
            # (hint: Associated versions share parent)
            latest_versions = {
                version["parent"]: version
                for version in all_versions
            }

            for version in all_versions:
                parent = version["parent"]
                highest = latest_versions[parent]["name"]
                if version["name"] > highest:
                    latest_versions[parent] = version

            representations = io.find({
                "type": "representation",
                "parent": {"$in": [v["_id"] for v in latest_versions.values()]}
            })

            for representation in representations:
                name = representation["name"]

                # TODO(marcus): These are permanently excluded
                # for now, but look towards making this customisable.
                if name in ("json", "source"):
                    continue

                if name not in representations_by_name:
                    representations_by_name[name] = list()

                representations_by_name[name].append(representation)

            # Prevent accidental load of subsets missing any one representation
            for name in representations_by_name.copy():
                if len(representations_by_name[name]) != len(subsets):
                    representations_by_name.pop(name)
                    self.echo("'%s' missing from some subsets." % name)

        else:
            version_document = version_item.data(DocumentRole)
            self.data["state"]["context"]["version"] = version_document["name"]

            # NOTE(marcus): This is backwards compatible with assets published
            # before locations were implemented. Newly published assets are
            # embedded with this attribute, but current ones were not.
            locations = version_document.get("locations", [])

            self.data["state"]["locations"][:] = locations

            representations_by_name = {
                representation["name"]: [representation]
                for representation in io.find(
                    {"type": "representation",
                     "parent": version_document["_id"]})
                if representation["name"] not in ("json", "source")
            }

            self.data["label"]["commentContainer"].show()
            comment = self.data["label"]["comment"]
            comment.setText(
                version_document["data"].get("comment") or "No comment"
            )

            self.data["label"]["sourceContainer"].show()
            source = self.data["label"]["source"]
            source.setText(version_document["data"].get("source", "No source"))

            self.data["label"]["createdContainer"].show()
            t = version_document["data"]["time"]
            t = datetime.datetime.strptime(t, "%Y%m%dT%H%M%SZ")
            t = datetime.datetime.strftime(t, "%b %d %Y %I:%M%p")
            created = self.data["label"]["created"]
            created.setText(t + " GMT")

        has = {"children": False}

        for name, documents in representations_by_name.items():
            # TODO(marcus): Separate this into something the
            # supervisor can configure.
            item = QtWidgets.QListWidgetItem({
                "ma": "Maya Ascii",
                "source": "Original Source File",
                "abc": "Pointcache",
                "history": "History",
                "curves": "Animation Curves",
            }.get(name, name))  # Default to using name as-is

            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(RepresentationsRole, documents)
            representations_model.addItem(item)
            has["children"] = True

        representations_model.setCurrentRow(0)

        if not has["children"]:
            item = QtWidgets.QListWidgetItem("No representations found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            representations_model.addItem(item)

        self.echo("Duration: %.3fs" % (time.time() - t1))

    def _representationschanged(self):
        load_button = self.data["button"]["load"]
        load_button.setEnabled(False)

        model = self.data["model"]["representations"]
        item = model.currentItem()

        if item is None:
            return

        if not item.data(QtCore.Qt.ItemIsEnabled):
            return

        # Update state
        document = item.data(RepresentationsRole)[0]
        self.data["state"]["context"]["representation"] = document["name"]

        template = self.data["state"]["template"]
        context = self.data["state"]["context"]
        path = template.format(**context)

        if os.path.exists(path):
            load_button.setEnabled(True)
        else:
            load_button.setToolTip("%s not found." % path)

    def on_load_pressed(self):
        models = self.data["model"]
        representations_model = models["representations"]
        representation_item = representations_model.currentItem()

        if representation_item is None:
            return

        for document in representation_item.data(RepresentationsRole):
            try:
                api.registered_host().load(representation=document["_id"])

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

            if self.data["button"]["autoclose"].checkState():
                self.close()

    def echo(self, message):
        widget = self.data["label"]["message"]
        widget.setText(str(message))
        widget.show()
        print(message)

        lib.schedule(widget.hide, 5000, channel="message")

    def closeEvent(self, event):
        # Kill on holding SHIFT
        modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
        shift_pressed = QtCore.Qt.ShiftModifier & modifiers

        if shift_pressed:
            print("Force quitted..")
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Kill on holding SHIFT
        modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
        shift_pressed = QtCore.Qt.ShiftModifier & modifiers

        if shift_pressed:
            print("Force quitted..")
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        print("Good bye")
        return super(Window, self).closeEvent(event)


def show(root=None, debug=False, parent=None):
    """Display Loader GUI

    Arguments:
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    # Remember window
    if module.window is not None:
        try:
            return module.window.show()
        except RuntimeError as e:
            if not e.message.rstrip().endswith("already deleted."):
                raise

            # Garbage collected
            module.window = None

    if debug:
        import traceback
        sys.excepthook = lambda typ, val, tb: traceback.print_last()

        io.install()

        any_project = next(
            project for project in io.projects()
            if project.get("active", True) is not False
        )

        io.activate_project(any_project)
        module.project = any_project["name"]

    with lib.application():
        window = Window(parent)
        window.show()

        window.refresh()

        module.window = window
