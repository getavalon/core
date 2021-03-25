import os
from .. import style
from ..vendor.Qt import QtWidgets, QtCore, QtGui, QtSvg


class DeselectableTreeView(QtWidgets.QTreeView):
    """A tree view that deselects on clicking on an empty area in the view"""

    def mousePressEvent(self, event):

        index = self.indexAt(event.pos())
        if not index.isValid():
            # clear the selection
            self.clearSelection()
            # clear the current index
            self.setCurrentIndex(QtCore.QModelIndex())

        QtWidgets.QTreeView.mousePressEvent(self, event)


class TreeViewSpinner(QtWidgets.QTreeView):
    size = 160

    def __init__(self, parent=None):
        super(TreeViewSpinner, self).__init__(parent=parent)

        loading_image_path = os.path.join(
            os.path.dirname(os.path.abspath(style.__file__)),
            "svg",
            "spinner-200.svg"
        )
        self.spinner = QtSvg.QSvgRenderer(loading_image_path)

        self.is_loading = False
        self.is_empty = True

    def paint_loading(self, event):
        rect = event.rect()
        rect = QtCore.QRectF(rect.topLeft(), rect.bottomRight())
        rect.moveTo(
            rect.x() + rect.width() / 2 - self.size / 2,
            rect.y() + rect.height() / 2 - self.size / 2
        )
        rect.setSize(QtCore.QSizeF(self.size, self.size))
        painter = QtGui.QPainter(self.viewport())
        self.spinner.render(painter, rect)

    def paint_empty(self, event):
        painter = QtGui.QPainter(self.viewport())
        rect = event.rect()
        rect = QtCore.QRectF(rect.topLeft(), rect.bottomRight())
        qtext_opt = QtGui.QTextOption(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
        )
        painter.drawText(rect, "No Data", qtext_opt)

    def paintEvent(self, event):
        if self.is_loading:
            self.paint_loading(event)
        elif self.is_empty:
            self.paint_empty(event)
        else:
            super(TreeViewSpinner, self).paintEvent(event)


class AssetsView(TreeViewSpinner, DeselectableTreeView):
    """Item view.
    This implements a context menu.
    """

    def __init__(self):
        super(AssetsView, self).__init__()
        self.setIndentation(15)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setHeaderHidden(True)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ShiftModifier:
                return
            elif modifiers == QtCore.Qt.ControlModifier:
                return

        super(AssetsView, self).mousePressEvent(event)
