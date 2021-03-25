from .lib import RegisteredRoots
from ..loader.widgets import SubsetWidget
from ...vendor.Qt import QtWidgets


class LibrarySubsetWidget(SubsetWidget):
    def on_copy_source(self):
        """Copy formatted source path to clipboard"""
        source = self.data.get("source", None)
        if not source:
            return

        project_name = self.dbcon.Session["AVALON_PROJECT"]
        root = RegisteredRoots.registered_root(project_name)
        if root:
            path = source.format(root=root)
        else:
            path = source
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(path)
