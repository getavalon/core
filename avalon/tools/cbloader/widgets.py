import datetime
import pprint
import inspect

from ...vendor.Qt import QtWidgets, QtCore, QtGui
from ...vendor import qtawesome
from ... import io
from ... import api

from .model import SubsetsModel
from .delegates import PrettyTimeDelegate, VersionDelegate
from . import lib


def _get_representations(version_id):
    """Return available representations representations for a version"""
    return [representation for representation in
            io.find({"type": "representation", "parent": version_id})
            if representation["name"] not in ("json", "source")]


class SubsetWidget(QtWidgets.QWidget):
    """A widget that lists the published subsets for an asset"""

    active_changed = QtCore.Signal()    # active index changed
    version_changed = QtCore.Signal()   # version state changed for a subset

    def __init__(self, parent=None):
        super(SubsetWidget, self).__init__(parent=parent)
        model = SubsetsModel()
        view = QtWidgets.QTreeView()
        view.setModel(model)

        view.setIndentation(5)
        view.setStyleSheet("""
            QTreeView::item{
                padding: 5px 1px;
                border: 0px;
            }
        """)
        view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        view.setSortingEnabled(True)
        view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        view.setAlternatingRowColors(True)

        # Set view delegates
        time_delegate = VersionDelegate()
        column = model.COLUMNS.index("version")
        view.setItemDelegateForColumn(column, time_delegate)

        version_delegate = PrettyTimeDelegate()
        column = model.COLUMNS.index("time")
        view.setItemDelegateForColumn(column, version_delegate)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        self.data = {
            "delegates": {
                "version": version_delegate,
                "time": time_delegate
            }
        }
        self.model = model
        self.view = view

        view.customContextMenuRequested.connect(self.on_context_menu)

        selection = view.selectionModel()
        selection.selectionChanged.connect(self.active_changed)

    def on_context_menu(self, point):

        point_index = self.view.indexAt(point)
        if not point_index.isValid():
            return

        # Get all representation->loader combinations available for the
        # index under the cursor, so we can list the user the options.
        loaders = list()
        node = point_index.data(self.model.NodeRole)
        version_id = node['version_document']['_id']
        for representation in _get_representations(version_id):
            for loader in lib.iter_loaders(representation["_id"]):
                loaders.append((representation, loader))

        if not loaders:
            # no loaders available
            self.echo("No compatible loaders available for this version.")
            return

        def sorter(value):
            """Sort the Loaders by their order and then their name"""
            Plugin = value[1]
            return Plugin.order, Plugin.__name__

        # List the available loaders
        menu = QtWidgets.QMenu(self)
        for representation, loader in sorted(loaders, key=sorter):

            # Label
            label = getattr(loader, "label", None)
            if label is None:
                label = loader.__name__

            # Add the representation as suffix
            label = "{0} ({1})".format(label, representation['name'])

            action = QtWidgets.QAction(label, menu)
            action.setData((representation, loader))

            # Add tooltip and statustip from Loader docstring
            tip = inspect.getdoc(loader)
            if tip:
                action.setToolTip(tip)
                action.setStatusTip(tip)

            # Support font-awesome icons using the `.icon` and `.icon_color`
            # attributes on plug-ins.
            icon = getattr(loader, "icon", None)
            if icon is not None:
                try:
                    key = "fa.{0}".format(icon)
                    color = getattr(loader, "icon_color", "white")
                    action.setIcon(qtawesome.icon(key, color=color))
                except Exception as e:
                    print("Unable to set icon for loader "
                          "{}: {}".format(loader, e))

            menu.addAction(action)

        # Show the context action menu
        global_point = self.view.mapToGlobal(point)
        action = menu.exec_(global_point)
        if not action:
            return

        # Find the representation name and loader to trigger
        action_representation, loader = action.data()
        representation_name = action_representation['name']  # extension

        # Run the loader for all selected indices, for those that have the
        # same representation available
        selection = self.view.selectionModel()
        rows = selection.selectedRows(column=0)

        # Ensure active point index is also used as first column so we can
        # correctly push it to the end in the rows list.
        point_index = point_index.sibling(point_index.row(), 0)

        # Ensure point index is run first.
        try:
            rows.remove(point_index)
        except ValueError:
            pass
        rows.insert(0, point_index)

        # Trigger
        for row in rows:
            node = row.data(self.model.NodeRole)
            version_id = node['version_document']['_id']
            representation = io.find_one({"type": "representation",
                                          "name": representation_name,
                                          "parent": version_id})
            if not representation:
                self.echo("Subset '{}' has no representation '{}'".format(
                        node['subset'],
                        representation_name
                ))
                continue

            # If the representation can be
            context = lib.get_representation_context(representation["_id"])
            if not lib.is_compatible_loader(loader, context):
                self.echo("Loader not compatible with '{}'".format(
                        node['subset']
                ))
                continue

            lib.run_loader(loader, representation['_id'])

    def echo(self, message):
        print(message)


class VersionTextEdit(QtWidgets.QTextEdit):
    """QTextEdit that displays version specific information.
    
    This also overrides the context menu to add actions like copying
    source path to clipboard or copying the raw data of the version
    to clipboard.
    
    """
    def __init__(self, parent=None):
        super(VersionTextEdit, self).__init__(parent=parent)

        self.data = {
            "source": None,
            "raw": None
        }

        # Reset
        self.set_version(None)

    def set_version(self, version_id):

        if not version_id:
            # Reset state to empty
            self.data = {
                "source": None,
                "raw": None,
            }
            self.setText("")
            self.setEnabled(True)
            return

        self.setEnabled(True)

        version = io.find_one({"_id": version_id, "type": "version"})
        assert version, "Not a valid version id"

        subset = io.find_one({"_id": version['parent'], "type": "subset"})
        assert subset, "No valid subset parent for version"

        # Define readable creation timestamp
        created = version["data"]["time"]
        created = datetime.datetime.strptime(created, "%Y%m%dT%H%M%SZ")
        created = datetime.datetime.strftime(created, "%b %d %Y %I:%M%p")

        comment = version['data'].get("comment", None) or "No comment"

        source = version['data'].get("source", None)
        source_label = source if source else "No source"

        # Store source and raw data
        self.data['source'] = source
        self.data['raw'] = version

        data = {
            "subset": subset['name'],
            "version": version['name'],
            "comment": comment,
            "created": created,
            "source": source_label
        }

        self.setHtml("""
<h3>{subset} v{version:03d}</h3>
<b>Comment</b><br>
{comment}<br>
<br>
<b>Created</b><br>
{created}<br>
<br>
<b>Source</b><br>
{source}<br>""".format(**data))

    def contextMenuEvent(self, event):
        """Context menu with additional actions"""
        menu = self.createStandardContextMenu()

        # Add additional actions when any text so we can assume
        # the version is set.
        if self.toPlainText().strip():

            menu.addSeparator()
            action = QtWidgets.QAction("Copy source path to clipboard",
                                       menu)
            action.triggered.connect(self.on_copy_source)
            menu.addAction(action)

            action = QtWidgets.QAction("Copy raw data to clipboard",
                                       menu)
            action.triggered.connect(self.on_copy_raw)
            menu.addAction(action)

        menu.exec_(event.globalPos())
        del menu

    def on_copy_source(self):
        """Copy formatted source path to clipboard"""
        source = self.data.get("source", None)
        if not source:
            return

        path = source.format(root=api.registered_root())
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(path)

    def on_copy_raw(self):
        """Copy raw version data to clipboard
        
        The data is string formatted with `pprint.pformat`.
        
        """
        raw = self.data.get("raw", None)
        if not raw:
            return

        raw_text = pprint.pformat(raw)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(raw_text)


class VersionWidget(QtWidgets.QWidget):
    """A Widget that display information about a specific version"""
    def __init__(self, parent=None):
        super(VersionWidget, self).__init__(parent=parent)

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Version")
        data = VersionTextEdit()
        data.setReadOnly(True)
        layout.addWidget(label)
        layout.addWidget(data)

        self.data = data

    def set_version(self, version_id):
        self.data.set_version(version_id)
