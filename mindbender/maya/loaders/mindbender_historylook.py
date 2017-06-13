from maya import cmds
from mindbender import api


class HistoryLookLoader(api.Loader):
    """Specific loader for lookdev"""

    families = ["mindbender.historyLookdev"]
    representations = ["ma"]

    def process(self, name, namespace, context):
        from mindbender import maya
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
