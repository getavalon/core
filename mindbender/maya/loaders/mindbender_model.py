from maya import cmds
from mindbender import api, maya


class ModelLoader(api.Loader):
    """Load models

    Stores the imported asset in a container named after the asset.

    """

    families = ["mindbender.model"]

    def process(self, project, asset, subset, version, representation):
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

        namespace = maya.unique_namespace(asset["name"], suffix="_")
        name = subset["name"]

        with maya.maintained_selection():
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

        # Assign default shader to meshes
        meshes = cmds.ls(nodes, type="mesh")
        cmds.sets(meshes, forceElement="initialShadingGroup")

        return nodes
