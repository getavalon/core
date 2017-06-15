
from ... import io
from ..projectmanager.model import (
    TreeModel,
    Node
)
from ..projectmanager import style
from ...vendor.Qt import QtCore
from ...vendor import qtawesome as qta


class SubsetsModel(TreeModel):
    COLUMNS = ["subset",
               "family",
               "version",
               "time",
               "author",
               "frames",
               "duration",
               "handles",
               "step"]

    def __init__(self, parent=None):
        super(SubsetsModel, self).__init__(parent=parent)
        self._asset_id = None
        self._icons = {
            "subset": qta.icon("fa.file-o", color=style.default)
        }

    def set_asset(self, asset_id):
        self._asset_id = asset_id
        self.refresh()

    def refresh(self):

        self.clear()
        if not self._asset_id:
            return

        parent = self._asset_id

        for subset in io.find({"type": "subset", "parent": parent}):

            last_version = io.find_one({"type": "version",
                                        "parent": subset['_id']},
                                       sort=[("name", -1)])
            if not last_version:
                # No published version for the subset
                continue

            data = subset.copy()

            # TODO(roy): Support switching "version" by the user
            data['subset'] = data['name']
            data['version'] = last_version['name']
            data['version_document'] = last_version

            # Get the data from the version
            version_data = last_version.get("data", dict())
            data['author'] = version_data.get("author", None)
            data['time'] = version_data.get("time", None)
            data["family"] = version_data.get("families", ["<unknown>"])[0]

            # Compute frame ranges (if data is present)
            start = version_data.get("startFrame", None)
            end = version_data.get("endFrame", None)
            handles = version_data.get("handles", None)
            if start is not None and end is not None:
                frames = "{0}-{1}".format(start, end)
                duration = end - start + 1
            else:
                frames = None
                duration = None

            data['startFrame'] = start
            data['endFrame'] = end
            data['duration'] = duration
            data['handles'] = handles
            data['frames'] = frames
            data['step'] = version_data.get("step", None)

            node = Node()
            node.update(data)
            self.add_child(node)

    def data(self, index, role):

        # Add icon to subset column
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return self._icons['subset']

        return super(SubsetsModel, self).data(index, role)
