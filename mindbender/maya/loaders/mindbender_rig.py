from mindbender import api
from mindbender.maya import lib, pipeline

from maya import cmds


class RigLoader(api.Loader):
    """Specific loader for rigs

    This automatically creates an instance for animators upon load.

    """

    families = ["mindbender.rig"]

    def process(self, asset, subset, version, representation):
        fname = representation["path"].format(
            dirname=version["path"].format(root=api.registered_root()),
            format=representation["format"]
        )

        namespace = lib.unique_namespace(asset["name"], suffix="_")
        name = subset["name"]

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
                              asset=asset,
                              subset=subset,
                              version=version,
                              representation=representation)

        # TODO(marcus): We are hardcoding the name "out_SET" here.
        #   Better register this keyword, so that it can be used
        #   elsewhere, such as in the Integrator plug-in,
        #   without duplication.
        output = next((node for node in nodes
                      if node.endswith("out_SET")), None)
        assert output, "No output in rig, this is a bug."

        with lib.maintained_selection():
            # Select contents of output
            cmds.select(output, noExpand=False)

            # TODO(marcus): Hardcoding the exact family here.
            #   Better separate the relationship between loading
            #   rigs and automatically assigning an instance to it.
            pipeline.create(name=lib.unique_name(asset["name"], suffix="_SET"),
                            family="mindbender.animation",
                            options={"useSelection": True})

        return nodes
