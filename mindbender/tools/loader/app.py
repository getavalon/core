import os
import sys
import time
import errno
import shutil
import tempfile
import threading
import Queue as queue

from ...vendor import requests
from ...vendor.Qt import QtWidgets, QtCore
from ... import api, io
from .. import lib
from ..awesome import tags as awesome

module = sys.modules[__name__]
module.window = None
module.root = api.registered_root()
module.project = os.getenv("MINDBENDER_PROJECT")
module.debug = bool(os.getenv("MINDBENDER_DEBUG"))

# About to be downloaded
module._downloads = queue.Queue()

# Which downloads are in progress?
module._downloading = dict()

# Custom roles
DocumentRole = QtCore.Qt.UserRole + 1
RepresentationsRole = QtCore.Qt.UserRole + 2
LatestRole = QtCore.Qt.UserRole + 3
LocationRole = QtCore.Qt.UserRole + 4


def download(src, dst):
    basename = os.path.basename(src)
    tmp = os.path.join(tempfile.gettempdir(), basename)

    try:
        response = requests.get(
            src,
            stream=True,
            auth=requests.auth.HTTPBasicAuth("location", "mypass")
        )
    except requests.ConnectionError as e:
        yield None, e
        return

    with open(tmp, "wb") as f:

        total_length = response.headers.get("content-length")

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            downloaded = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                downloaded += len(data)
                f.write(data)

                if module.debug:
                    time.sleep(0.007)

                yield int(100.0 * downloaded / total_length), None

    try:
        os.makedirs(os.path.dirname(dst))
    except OSError as e:
        # An already existing working directory is fine.
        if e.errno != errno.EEXIST:
            raise

    shutil.copy(tmp, dst)

    # Clean up
    os.remove(tmp)


class Window(QtWidgets.QDialog):
    """Asset loader interface"""

    download_progressed = QtCore.Signal(str, int)
    download_completed = QtCore.Signal()
    download_errored = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle(
            "Asset Loader 2.0 - %s/%s" % (
                module.root, module.project))

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        body = QtWidgets.QWidget()
        sidepanel = QtWidgets.QWidget()
        sidepanel.setFixedWidth(200)
        footer = QtWidgets.QWidget()
        footer.setFixedHeight(20)

        container = QtWidgets.QWidget()

        assets = QtWidgets.QListWidget()
        subsets = QtWidgets.QListWidget()
        versions = QtWidgets.QListWidget()
        representations = QtWidgets.QListWidget()

        # Enable loading many subsets at once
        subsets.setSelectionMode(subsets.ExtendedSelection)

        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(assets)
        layout.addWidget(subsets)
        layout.addWidget(versions)
        layout.addWidget(representations)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)

        autoclose_checkbox = QtWidgets.QCheckBox("Auto-close")
        autoclose_checkbox.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(autoclose_checkbox, 1, 0)

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(container)
        layout.addWidget(sidepanel)
        layout.setContentsMargins(0, 0, 0, 0)

        load_button = QtWidgets.QPushButton("Load")
        refresh_button = QtWidgets.QPushButton(awesome["refresh"])
        refresh_button.setStyleSheet("""
QPushButton {
    max-width: 30px;
    font-family: "FontAwesome";
}
""")

        offline_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        offline_slider.setRange(0, 1)
        offline_slider.setFixedHeight(25)
        offline_slider.setStyleSheet("""
QSlider::groove:horizontal {
    border: 1px solid #666;
    height: 23px;
    background: #777;
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::groove:horizontal:enabled {
    border: 1px solid #222;
    height: 23px;
    background: qlineargradient(x1:0, y1:0, \
                                x2:0, y2:1, \
                                stop:0 #555, \
                                stop:1 #666);
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #777;
    border: 1px solid #555;
    width: 45px;
    margin: 1px;
    border-radius: 2px;
}

QSlider::handle:horizontal:enabled {
    border: 1px solid #333;
    background: qlineargradient(x1:0, y1:0, \
                                x2:1, y2:1, \
                                stop:0 #aaa \
                                stop:1 #888);
}

""")
        offline_label = QtWidgets.QLabel("Available offline..")
        offline_on = QtWidgets.QLabel("On", offline_slider)
        offline_off = QtWidgets.QLabel("Off", offline_slider)
        offline_on.move(72, 6)
        offline_off.move(16, 6)

        for toggle in (offline_on, offline_off):
            toggle.show()
            toggle.setStyleSheet("QLabel { color: black; }")

        offline = QtWidgets.QWidget()

        layout = QtWidgets.QHBoxLayout(offline)
        layout.addWidget(offline_label)
        layout.addWidget(offline_slider)
        layout.setContentsMargins(0, 0, 0, 0)

        message = QtWidgets.QLabel()
        message.hide()

        # side_header = QtWidgets.QLabel("Asset A")
        # side_header.setStyleSheet("QLabel { font: bold 15px; }")

        # side_title = QtWidgets.QLabel("Some Title")
        # side_body = QtWidgets.QLabel("A very long body here..")

        # side_comment_header = QtWidgets.QLabel("Comment")
        # side_comment = QtWidgets.QLabel("An optional comment here")

        buttons = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(buttons)
        layout.addWidget(refresh_button)
        layout.addWidget(load_button, 5)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(sidepanel)
        # layout.addWidget(side_header)
        # layout.addWidget(side_title)
        # layout.addWidget(side_body)
        # layout.addWidget(side_comment_header)
        # layout.addWidget(side_comment)
        layout.addWidget(QtWidgets.QWidget(), 1)
        layout.addWidget(options, 0, QtCore.Qt.AlignBottom)
        layout.addWidget(offline)
        layout.addWidget(buttons)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(footer)
        layout.addWidget(message)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.data = {
            "button": {
                "load": load_button,
                "autoclose": autoclose_checkbox,
                "offline": offline_slider,
            },
            "model": {
                "assets": assets,
                "subsets": subsets,
                "versions": versions,
                "representations": representations,
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

        self.download_progressed.connect(self.on_download_progressed)
        self.download_completed.connect(self.on_download_completed)
        self.download_errored.connect(self.on_download_errored)

        offline_slider.valueChanged.connect(self.on_make_available_offline)
        load_button.clicked.connect(self.on_load_pressed)
        refresh_button.clicked.connect(self.on_refresh_pressed)
        assets.currentItemChanged.connect(self.on_assetschanged)
        subsets.itemSelectionChanged.connect(self.on_subsetschanged)
        versions.currentItemChanged.connect(self.on_versionschanged)
        representations.currentItemChanged.connect(
            self.on_representationschanged)

        # Defaults
        self.resize(1100, 600)

        load_button.setEnabled(False)
        offline_slider.setEnabled(False)

        thread = threading.Thread(target=self._download_manager)
        thread.daemon = True
        thread.start()

    def _download_manager(self):
        while True:
            src, dst = module._downloads.get()

            # Killswitch
            if not any([src, dst]):
                break

            for progress, error in download(src, dst):

                if error:
                    self.download_errored.emit(
                        "ERROR: Could not download %s" % src)
                    break

                self.download_progressed.emit(src, progress)

            module._downloading.pop(dst)

            if not error:
                self.download_completed.emit()

    def on_download_progressed(self, fname, progress):
        self.echo("Downloading %s.. %d%%" % (fname, progress))

    def on_download_completed(self):
        self._representationschanged()
        self.echo("Done")

    def on_download_errored(self, message):
        self._representationschanged()
        self.echo(message)

    def on_make_available_offline(self, state):
        assert len(self.data["state"]["locations"]), (
            "Must have at least one location"
        )

        if state != 1:
            return

        if not self.data["button"]["offline"].isEnabled():
            return

        models = self.data["model"]
        representations_model = models["representations"]
        representation_item = representations_model.currentItem()
        location = self.data["state"]["locations"][0]

        for representation in representation_item.data(RepresentationsRole):
            try:
                template = self.data["state"]["template"]
                context = self.data["state"]["context"].copy()
                context["root"] = location
                path = template.format(**context)

            except Exception as e:
                print(e)

            else:
                context = self.data["state"]["context"]

                src = path
                dst = template.format(**context)

                module._downloads.put((src, dst))
                module._downloading[dst] = True

        offline = self.data["button"]["offline"]
        offline.setEnabled(False)

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

    def on_subsetschanged(self, *args):
        self.echo("Fetching results..")
        lib.schedule(self._subsetschanged, 100, channel="mongo")

    def on_versionschanged(self, *args):
        self.echo("Fetching results..")
        lib.schedule(self._versionschanged, 100, channel="mongo")

    def on_representationschanged(self, *args):
        lib.schedule(self._representationschanged, 100, channel="mongo")

    # ------------------------------

    def _refresh(self):
        """Load assets from disk and add them to a QListView"""

        assets_model = self.data["model"]["assets"]
        assets_model.clear()

        has = {"children": False}

        project = io.find_one({"type": "project"})

        assert project, "This is a bug"

        assets = io.find({"type": "asset", "parent": project["_id"]})
        for asset in sorted(assets, key=lambda i: i["name"]):
            item = QtWidgets.QListWidgetItem(asset["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(DocumentRole, asset)
            assets_model.addItem(item)
            has["children"] = True

        if not has["children"]:
            item = QtWidgets.QListWidgetItem("No assets found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            assets_model.addItem(item)

        assets_model.setFocus()
        assets_model.setCurrentRow(0)

        # Update state
        state = self.data["state"]
        state["template"] = project["config"]["template"]["publish"]
        state["context"]["root"] = api.registered_root()
        state["context"]["project"] = project["name"]

        self.data["button"]["load"].setEnabled(False)

    def _assetschanged(self):
        assets_model = self.data["model"]["assets"]
        subsets_model = self.data["model"]["subsets"]

        subsets_model.clear()

        t1 = time.time()

        asset_item = assets_model.currentItem()

        # The model is empty
        if asset_item is None:
            return

        document = asset_item.data(DocumentRole)

        # The model contains an empty item
        if document is None:
            return

        has = {"children": False}

        for child in io.find({"type": "subset",
                              "parent": document["_id"]}):
            item = QtWidgets.QListWidgetItem(child["name"])
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(DocumentRole, child)
            item.setData(LocationRole, document.get("locations", []))
            subsets_model.addItem(item)
            has["children"] = True

        if not has["children"]:
            item = QtWidgets.QListWidgetItem("No subsets found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            subsets_model.addItem(item)

        self.data["state"]["context"]["asset"] = document["name"]
        self.data["state"]["context"]["silo"] = document["silo"]
        self.echo("Duration: %.3fs" % (time.time() - t1))

    def _subsetschanged(self):
        subsets_model = self.data["model"]["subsets"]
        versions_model = self.data["model"]["versions"]

        versions_model.clear()

        t1 = time.time()

        has = {"children": False}

        if len(subsets_model.selectedItems()) == 0:
            has["children"] = False

        elif len(subsets_model.selectedItems()) > 1:
            item = QtWidgets.QListWidgetItem("Latest")
            item.setData(QtCore.Qt.ItemIsEnabled, True)
            item.setData(LatestRole, True)
            versions_model.addItem(item)
            versions_model.setCurrentItem(item)
            has["children"] = True

        else:
            subset_item = subsets_model.currentItem()

            if not subset_item.data(QtCore.Qt.ItemIsEnabled):
                return

            document = subset_item.data(DocumentRole)
            self.data["state"]["context"]["subset"] = document["name"]

            for child in io.find({"type": "version",
                                  "parent": document["_id"]},
                                 sort=[("name", -1)]):
                item = QtWidgets.QListWidgetItem("v%03d" % child["name"])
                item.setData(QtCore.Qt.ItemIsEnabled, True)
                item.setData(DocumentRole, child)
                versions_model.addItem(item)
                has["children"] = True

            versions_model.setCurrentRow(0)

        if not has["children"]:
            item = QtWidgets.QListWidgetItem("No versions found")
            item.setData(QtCore.Qt.ItemIsEnabled, False)
            versions_model.addItem(item)

        self.echo("Duration: %.3fs" % (time.time() - t1))

    def _versionschanged(self):
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
            document = version_item.data(DocumentRole)
            self.data["state"]["context"]["version"] = document["name"]

            # NOTE(marcus): This is backwards compatible with assets published
            # before locations were implemented. Newly published assets are
            # embedded with this attribute, but current ones were not.
            locations = document.get("locations", [])

            self.data["state"]["locations"][:] = locations

            representations_by_name = {
                representation["name"]: [representation]
                for representation in io.find({"type": "representation",
                                               "parent": document["_id"]})
                if representation["name"] not in ("json", "source")
            }

        has = {"children": False}

        for name, documents in representations_by_name.items():
            item = QtWidgets.QListWidgetItem({
                "ma": "Maya Ascii",
                "source": "Original source file",
                "abc": "Alembic"
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
        offline = self.data["button"]["offline"]
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

        offline.setEnabled(False)

        if path in module._downloading or os.path.exists(path):
            offline.setValue(1)
            load_button.setEnabled(True)
            offline.setToolTip("Already available offline.")

        else:
            offline.setValue(0)

            # Is the representation available at any location?
            if len(self.data["state"]["locations"]) > 0:
                offline.setEnabled(True)
                offline.setToolTip("Toggle to make available offline.")

            else:
                offline.setToolTip("Couldn't find where to "
                                   "download this from..")

    def on_refresh_pressed(self):
        self.refresh()

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
        # Kill download manager
        module._downloads.put((None, None))

        print("Good bye")
        return super(Window, self).closeEvent(event)


def show(root=None, debug=False):
    """Display Loader GUI

    Arguments:
        debug (bool, optional): Run loader in debug-mode,
            defaults to False

    """

    try:
        module.window.close()
        del module.window
    except (RuntimeError, AttributeError):
        pass

    if debug:
        import traceback
        sys.excepthook = lambda typ, val, tb: traceback.print_last()

        io.install()

        any_project = next(io.projects())
        io.activate_project(any_project)
        module.project = any_project["name"]

    with lib.application():
        window = Window()
        window.show()

        window.refresh()

        module.window = window
