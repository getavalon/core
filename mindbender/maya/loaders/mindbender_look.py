import json

from maya import cmds
from mindbender import api, maya


class LookLoader(api.Loader):
    """Specific loader for lookdev"""

    families = ["mindbender.lookdev"]

    def process(self, asset, subset, version, representation):
        fname = representation["path"].format(
            dirname=version["path"].format(root=api.registered_root()),
            format=representation["format"]
        )

        namespace = asset["name"] + "_"
        name = maya.unique_name(subset["name"])

        with maya.maintained_selection():
            nodes = cmds.file(fname,
                              namespace=namespace,
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

            # Append namespace to shader group identifier.
            # E.g. `blinn1SG` -> `Bruce_:blinn1SG`
            relationships = {
                "%s:%s" % (namespace, shader): relationships[shader]
                for shader in relationships
            }

            maya.apply_shaders(relationships)

        return nodes
