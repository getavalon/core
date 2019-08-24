from avalon.vendor.Qt import QtCore
from avalon.vendor import qtawesome


class Main(QtCore.QAbstractTableModel):
    ContentRole = QtCore.Qt.UserRole + 0

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        self._items = []
        self._cache = {}

    def columnCount(self, index):
        return 2

    def rowCount(self, index):
        return len(self._items)

    def item(self, row=0):
        return self._items[row]

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return

        row = index.row()
        column = index.column()
        item = self._items[row]

        if role == self.ContentRole:
            try:
                return self._cache[index, role]

            except KeyError:
                if item["type"] == "section":
                    content = "\n".join(item["data"]["lines"])

                if item["type"] == "rule":
                    content = item["data"]["description"]

                self._cache[index, role] = content

            return content

        if column == 0:
            if role == QtCore.Qt.DisplayRole:
                return item.get("label", item["name"])

            if role == QtCore.Qt.DecorationRole:
                try:
                    return self._cache[index, role]

                except KeyError:  # Expensive
                    icon = qtawesome.icon(
                        "fa.folder"
                        if item["type"] == "section"
                        else "fa.file"
                    )

                    self._cache[index, role] = icon
                    return icon

        elif column == 1:
            if role == QtCore.Qt.DisplayRole and item["type"] == "rule":
                return item["data"]["severity"]

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            return

        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Label"

            if section == 1:
                return "Severity"

    def parseSections(self, lines):
        sections = []  # keys may not be unique
        section = None

        for line in lines:
            line = line.rstrip()

            if line.startswith("#"):
                if section:
                    sections += [section]

                # Start a new section
                header = line.strip("#").strip()
                id_ = header.lower().replace(" ", "-")
                section = {
                    "id": id_,
                    "header": header,
                    "level": line.count("#"),
                    "lines": []
                }

            elif section:
                section["lines"].append(line)

        return sections

    def parseRules(self, lines):
        rules = {}  # keys guaranteed to be unique

        for line in lines:
            line = line.rstrip()
            if not line.startswith("- **"):
                continue

            _, name, description = line.split(" ", 2)
            name = name.strip("*").rstrip("*")
            rules[name] = {
                "name": name,
                "description": description,
                "example": None,
                "severity": (
                    2 if "MUST" in description else
                    1 if "SHOULD" in description else
                    0
                )
            }

        return rules

    def reset(self, fname):
        with open(fname) as f:
            lines = f.readlines()

        sections = self.parseSections(lines)
        rules = self.parseRules(lines)

        for section in sections:
            self._items += [{
                "name": section["id"],
                "label": section["header"],
                "type": "section",
                "data": section,
            }]

        for name, rule in rules.items():
            self._items += [{
                "name": name,
                "type": "rule",
                "data": rule,
            }]
