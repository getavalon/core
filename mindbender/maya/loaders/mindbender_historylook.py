from maya import cmds
from mindbender import api, maya


class HistoryLookLoader(api.Loader):
    """Specific loader for lookdev"""

    families = ["mindbender.historyLookdev"]

    def process(self, asset, subset, version, representation):
        fname = representation["path"].format(
            dirname=version["path"].format(root=api.registered_root()),
            format=representation["format"]
        )

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
