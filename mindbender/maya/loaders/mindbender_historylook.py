from maya import cmds
from mindbender import api, maya


class HistoryLookLoader(api.Loader):
    """Specific loader for lookdev"""

    families = ["mindbender.historyLookdev"]

    def process(self, project, asset, subset, version, representation):
        template = project["config"]["template"]["publish"]
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

        namespace = asset["name"] + "_"
        name = maya.unique_name(subset["name"])

        with maya.maintained_selection():
            nodes = cmds.file(
                fname,
                namespace=namespace,
                reference=True,
                returnNewNodes=True,
                groupReference=True,
                groupName=namespace + ":" + name
            )

        # Containerising
        maya.containerise(
            name=name,
            namespace=namespace,
            nodes=nodes,
            asset=asset,
            subset=subset,
            version=version,
            representation=representation,
            loader=type(self).__name__
        )

        return nodes
