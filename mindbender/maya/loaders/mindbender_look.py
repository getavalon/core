import json

from mindbender import api
from mindbender.maya import lib, pipeline

from maya import cmds


class LookLoader(api.Loader):
    """Specific loader for lookdev"""

    families = ["mindbender.lookdev"]

    def process(self, asset, subset, version, representation):
        fname = representation["path"].format(
            dirname=version["path"].format(root=api.registered_root()),
            format=representation["format"]
        )

        namespace = asset["name"] + "_"
        name = lib.unique_name(subset["name"])

        with lib.maintained_selection():
            nodes = cmds.file(fname,
                              namespace=namespace,
                              reference=True,
                              returnNewNodes=True)

        # Containerising
        pipeline.containerise(name=name,
                              namespace=namespace,
                              nodes=nodes,
                              asset=asset,
                              subset=subset,
                              version=version,
                              representation=representation)

        # Assign shaders
        representation = next(
            (rep for rep in version["representations"]
                if rep["format"] == ".json"), None)

        if representation is None:
            cmds.warning("Look development asset has no relationship data.")

        else:
            path = representation["path"].format(
                dirname=version["path"].format(root=api.registered_root()),
                format=representation["format"]
            )

            with open(path) as f:
                relationships = json.load(f)

            lib.apply_shaders(relationships)

        return cmds.referenceQuery(nodes[0], referenceNode=True)
