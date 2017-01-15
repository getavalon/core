from mindbender import api
from mindbender.maya import pipeline

from maya import cmds


class AnimationLoader(api.Loader):
    """Specific loader for animation

    This names the resulting container after the subset, rather than asset

    """

    families = ["mindbender.animation"]

    def process(self, asset, subset, version, representation):

        cmds.loadPlugin("AbcImport.mll", quiet=True)

        fname = representation["path"].format(
            dirname=version["path"].format(root=api.registered_root()),
            format=representation["format"]
        )

        name = subset["name"]
        namespace = subset["name"] + "_"

        if cmds.objExists(namespace + ":" + name):
            cmds.warning("Asset already imported.")

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

        return cmds.referenceQuery(nodes[0], referenceNode=True)
