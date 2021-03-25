import json
from ...vendor.Qt import QtWidgets, QtCore


class InstanceDetail(QtWidgets.QWidget):
    save_triggered = QtCore.Signal()

    def __init__(self, parent=None):
        super(InstanceDetail, self).__init__(parent)

        details_widget = QtWidgets.QPlainTextEdit(self)
        save_btn = QtWidgets.QPushButton("Save", self)

        self._block_changes = False
        self._editable = False
        self._item_id = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(details_widget, 1)
        layout.addWidget(save_btn, 0, QtCore.Qt.AlignRight)

        save_btn.clicked.connect(self.on_save)
        details_widget.textChanged.connect(self._on_text_change)

        self.details_widget = details_widget
        self.save_btn = save_btn

        self.set_editable(False)

    def on_save(self):
        if self.is_valid():
            self.save_triggered.emit()

    def set_editable(self, enabled=True):
        self._editable = enabled
        self.update_state()

    def update_state(self, valid=None):
        editable = self._editable
        if not self._item_id:
            editable = False

        self.save_btn.setVisible(editable)
        self.details_widget.setReadOnly(not editable)
        if valid is None:
            valid = self.is_valid()

        style_sheet = ""
        if not valid:
            style_sheet = "border-color: #ff0000;"

        self.save_btn.setEnabled(valid)
        self.details_widget.setStyleSheet(style_sheet)

    def set_details(self, container, item_id):
        self._item_id = item_id

        text = "Nothing selected"
        if item_id:
            try:
                text = json.dumps(container, indent=4)
            except Exception:
                text = str(container)

        self._block_changes = True
        self.details_widget.setPlainText(text)
        self._block_changes = False

        self.update_state()

    def instance_data_from_text(self):
        try:
            jsoned = json.loads(self.details_widget.toPlainText())
        except Exception:
            jsoned = None
        return jsoned

    def item_id(self):
        return self._item_id

    def is_valid(self):
        if not self._item_id:
            return True

        value = self.details_widget.toPlainText()
        valid = False
        try:
            jsoned = json.loads(value)
            if jsoned and isinstance(jsoned, dict):
                valid = True

        except Exception:
            pass
        return valid

    def _on_text_change(self):
        if self._block_changes or not self._item_id:
            return

        valid = self.is_valid()
        self.update_state(valid)
