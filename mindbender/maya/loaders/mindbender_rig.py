from maya import cmds
from mindbender import api, maya


class RigLoader(api.Loader):
    """Specific loader for rigs

    This automatically creates an instance for animators upon load.

    """

    families = ["mindbender.rig"]

    def process(self, fname, name, namespace):
        nodes = cmds.file(fname,
                          namespace=namespace,
                          reference=True,
                          returnNewNodes=True,
                          groupReference=True,
                          groupName=namespace + ":" + name)

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

            # Assuming "myAsset_01_"
            # TODO(marcus): We'll need a better way of managing this..
            assert namespace.count("_") == 2, (
                "%s.count('_') != 2, This is a bug" % namespace)

            # TODO(marcus): Hardcoding the exact family here.
            #   Better separate the relationship between loading
            #   rigs and automatically assigning an instance to it.
            maya.create(asset=os.environ["MINDBENDER_ASSET"],
                        subset=maya.unique_name(asset["name"], suffix="_SET"),
                        family="mindbender.animation",
                        options={"useSelection": True})

        return nodes
