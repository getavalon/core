from maya import cmds
from mindbender import maya


class ModelLoader(maya.Loader):
    """Load models

    Stores the imported asset in a container named after the asset.

    """

    families = ["mindbender.model"]
    representations = ["ma"]

    def process(self, context):
        with maya.maintained_selection():
            nodes = cmds.file(
                self.fname,
                namespace=self.namespace,
                reference=True,
                returnNewNodes=True,
                groupReference=True,
                groupName=self.namespace + ":" + self.name
            )

        # Assign default shader to meshes
        meshes = cmds.ls(nodes, type="mesh")
        cmds.sets(meshes, forceElement="initialShadingGroup")

        return nodes
