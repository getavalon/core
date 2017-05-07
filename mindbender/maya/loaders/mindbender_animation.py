from maya import cmds
from mindbender import api, maya


class AnimationLoader(api.Loader):
    """Specific loader for animation

    This names the resulting container after the subset, rather than asset

    """

    families = ["mindbender.animation"]

    def process(self, project, asset, subset, version, representation):

        cmds.loadPlugin("AbcImport.mll", quiet=True)

        template = project["template"]["publish"]
        data = {
            "root": api.registered_root(),
            "project": project["name"],
            "asset": asset["name"],
            "silo": asset["silo"],
            "subset": subset["name"],
            "version": version["name"],
            "representation": representation["name"].strip("."),
        }

        fname = template.format(**data)

        name = subset["name"]
        namespace = subset["name"] + "_"

        if cmds.objExists(namespace + ":" + name):
            cmds.warning("Asset already imported.")

        nodes = cmds.file(fname,
                          namespace=namespace,

                          # Prevent identical alembic nodes
                          # from being shared.
                          sharedReferenceFile=False,

                          groupReference=True,
                          groupName=namespace + ":" + name,
                          reference=True,
                          returnNewNodes=True)

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
