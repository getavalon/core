from maya import cmds
from mindbender import maya


class HistoryLookLoader(maya.Loader):
    """Specific loader for lookdev"""

    families = ["mindbender.historyLookdev"]
    representations = ["ma"]

    def process(self, name, namespace, context):
        with maya.maintained_selection():
            nodes = cmds.file(
                self.fname,
                namespace=namespace,
                reference=True,
                returnNewNodes=True,
                groupReference=True,
                groupName=namespace + ":" + name
            )

        self[:] = nodes
