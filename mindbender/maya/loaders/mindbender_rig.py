import os
from maya import cmds
from mindbender import api, maya


class RigLoader(api.Loader):
    """Specific loader for rigs

    This automatically creates an instance for animators upon load.

    """

    families = ["mindbender.rig"]
    # name = "{subset}"
    # namespace = maya.Unique("{asset}")

    def process(self, project, asset, subset, version, representation):
        # def process(self, representation):
        # project, asset, subset, version = io.parenthood(representation)

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
        assert os.path.exists(fname), "%s does not exist" % fname

        namespace = maya.unique_namespace(asset["name"], suffix="_")
        name = subset["name"]

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

        # TODO(marcus): We are hardcoding the name "out_SET" here.
        #   Better register this keyword, so that it can be used
        #   elsewhere, such as in the Integrator plug-in,
        #   without duplication.
        output = next((node for node in nodes
                      if node.endswith("out_SET")), None)
        assert output, "No output in rig, this is a bug."

        with maya.maintained_selection():
            # Select contents of output
            cmds.select(output, noExpand=False)

            # TODO(marcus): Hardcoding the exact family here.
            #   Better separate the relationship between loading
            #   rigs and automatically assigning an instance to it.
            maya.create(name=maya.unique_name(asset["name"], suffix="_SET"),
                        family="mindbender.animation",
                        options={"useSelection": True})

        return nodes
