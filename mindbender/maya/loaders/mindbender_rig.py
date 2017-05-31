from maya import cmds
from mindbender import maya


class RigLoader(maya.Loader):
    """Specific loader for rigs

    This automatically creates an instance for animators upon load.

    """

    families = ["mindbender.rig"]
    representations = ["ma"]

    def process(self, context):
        nodes = cmds.file(self.fname,
                          namespace=self.namespace,
                          reference=True,
                          returnNewNodes=True,
                          groupReference=True,
                          groupName=self.namespace + ":" + self.name)

        # Store for post-process
        self.new_nodes[:] = nodes

        return nodes

    def post_process(self, context):
        nodes = self.new_nodes

        # TODO(marcus): We are hardcoding the name "out_SET" here.
        #   Better register this keyword, so that it can be used
        #   elsewhere, such as in the Integrator plug-in,
        #   without duplication.
        output = next(
            (node for node in nodes if node.endswith("out_SET")), None)
        controls = next(
            (node for node in nodes if node.endswith("controls_SET")), None)

        assert output, "No out_SET in rig, this is a bug."
        assert controls, "No controls_SET in rig, this is a bug."

        with maya.maintained_selection():
            cmds.select([output, controls], noExpand=True)

            dependencies = [context["representation"]["_id"]]
            asset = context["asset"]["name"] + "_"
            maya.create(
                name=maya.unique_name(asset, suffix="_SET"),
                family="mindbender.animation",
                options={"useSelection": True},
                data={
                    "dependencies": " ".join(str(d) for d in dependencies)
                })
