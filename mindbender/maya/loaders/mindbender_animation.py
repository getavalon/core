from maya import cmds
from mindbender import api, maya


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
        maya.containerise(name=name,
                          namespace=namespace,
                          nodes=nodes,
                          asset=asset,
                          subset=subset,
                          version=version,
                          representation=representation,
                          loader=type(self).__name__)

        return nodes
