from maya import cmds
from mindbender import api, maya


class ModelLoader(api.Loader):
    """Load models

    Stores the imported asset in a container named after the asset.

    """

    families = ["mindbender.model"]

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

        # Assign default shader to meshes
        meshes = cmds.ls(nodes, type="mesh")
        cmds.sets(meshes, forceElement="initialShadingGroup")

        return nodes
