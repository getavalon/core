from maya import cmds
from mindbender import api, maya


class HistoryLookLoader(api.Loader):
    """Specific loader for lookdev"""

    families = ["mindbender.historyLookdev"]

    def process(self, fname, name, namespace):
        with maya.maintained_selection():
            nodes = cmds.file(
                fname,
                namespace=namespace,
                reference=True,
                returnNewNodes=True,
                groupReference=True,
                groupName=namespace + ":" + name
            )

        return nodes
