import re
from collections import deque


def parse(script):
    """Parse Nuke node's TCL script string into nested list structure

    Args:
        script (str): Node knobs TCL script string

    Returns:
        Tablet: A list containing knob scripts or tab knobs that has parsed
            into list

    """
    queue = deque(script.split("\n"))
    tab = Tablet()
    tab.consume(queue)
    return tab


TYPE_NODE = 0
TYPE_KNOBS = 1
TYPE_GROUP = -2
TYPE_KNOBS_CLOSE = -1
TYPE_GROUP_CLOSE = -3

TAB_PATTERN = re.compile(
    'addUserKnob {20 '
    '(?P<name>\\S+)'
    '(| l (?P<label>".*"|\\S+))'
    '(| n (?P<type>1|-[1-3]))'
    '}'
)


class Tablet(list):
    """
    """

    def __init__(self, name=None, label=None, type=None, parent=None):
        self.name = name
        self.label = label
        self.type = type
        self.parent = parent
        self[:] = list()

        self.tab_closed = False
        self.not_in_group = type is not None and type != TYPE_GROUP

    def __eq__(self, other):
        return "@" + self.name == other

    def find_tab(self, name):
        """Return child tab if exists in list"""
        return next((item for item in self if item == "@" + name), None)

    def consume(self, queue):
        """
        """
        def under_root():
            return getattr(self.parent, "parent", None) is not None

        def ignore_tab_value(name):
            if queue and queue[0] == "%s 1" % name:
                queue.popleft()

        while queue:
            line = queue.popleft()
            if not line:
                continue

            matched = TAB_PATTERN.search(line)
            if matched:
                tab_profile = matched.groupdict()
                name = tab_profile["name"]
                label = tab_profile["label"]
                type = int(tab_profile["type"] or 0)
            else:
                self.append(line)
                continue

            ignore_tab_value(name)

            if type in (TYPE_KNOBS_CLOSE, TYPE_GROUP_CLOSE):
                self.parent.tab_closed = True
                return

            elif type == TYPE_NODE:
                if self.not_in_group:
                    queue.appendleft(line)
                    return

            tab = Tablet(name, label, type=type, parent=self)
            self.append(tab)

            tab.consume(queue)

            if self.tab_closed and under_root():
                return

    def merge(self, other):
        """
        """
        for item in other:
            if isinstance(item, Tablet):
                tab = self.find_tab(item.name)
                if tab is not None:
                    tab.merge(item)
                    continue

            self.append(item)

    def to_script(self, join=True):
        """
        """
        script = list()
        for item in self:
            if isinstance(item, Tablet):
                sub_script = item.to_script(join=False)

                line = "addUserKnob {20 " + item.name
                if item.label is not None:
                    line += " l " + item.label

                if item.type == TYPE_NODE:
                    sub_script.insert(0, line + "}")

                elif item.type == TYPE_KNOBS:
                    sub_script.insert(0, line + " n 1}")
                    sub_script.append(line + " n -1}")

                elif item.type == TYPE_GROUP:
                    sub_script.insert(0, line + " n -2}")
                    sub_script.append(line + " n -3}")

                script += sub_script
                continue

            script.append(item)

        return "\n".join(script) if join else script
