from mindbender import api
from mindbender.maya import lib, pipeline

from maya import cmds


class ModelLoader(api.Loader):
    """Load models

    Stores the imported asset in a container named after the asset.

    """

    families = ["mindbender.model"]

    def process(self, asset, subset, version, representation):
        fname = representation["path"].format(
            dirname=version["path"].format(root=api.registered_root()),
            format=representation["format"]
        )

        namespace = lib.unique_namespace(asset["name"], suffix="_")
        name = subset["name"]

        print("Loading %s" % fname)
        with lib.maintained_selection():
            nodes = cmds.file(fname,
                              namespace=namespace,
                              reference=True,
                              returnNewNodes=True,
                              groupReference=True,
                              groupName=namespace + ":" + name)

        # Containerising
        pipeline.containerise(name=name,
                              namespace=namespace,
                              nodes=nodes,
                              version=version)

        # Assign default shader to meshes
        meshes = cmds.ls(nodes, type="mesh")
        cmds.sets(meshes, forceElement="initialShadingGroup")

        return cmds.referenceQuery(nodes[0], referenceNode=True)
