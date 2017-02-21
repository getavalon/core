import pyblish.api


class SelectAssemblies(pyblish.api.Action):
    label = "Select Assemblies"
    on = "failed"

    def process(self, context, plugin):
        from maya import cmds
        cmds.select(plugin.assemblies)


class ValidateMindbenderSingleAssembly(pyblish.api.InstancePlugin):
    """Each asset must have a single top-level group

    The given instance is test-exported, along with construction
    history to test whether more than 1 top-level DAG node would
    be included in the exported file.

    """

    label = "Validate Single Assembly"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["mindbender.model", "mindbender.rig"]
    actions = [
        pyblish.api.Category("Actions"),
        SelectAssemblies,
    ]

    assemblies = []

    def process(self, instance):
        from maya import cmds
        from mindbender import maya

        with maya.maintained_selection():
            cmds.select(instance, replace=True)
            nodes = cmds.file(
                constructionHistory=True,
                exportSelected=True,
                preview=True,
                force=True,
            )

        self.assemblies[:] = cmds.ls(nodes, assemblies=True)

        if not self.assemblies:
            raise Exception("No assembly found.")

        if len(self.assemblies) != 1:
            self.assemblies = '"%s"' % '", "'.join(self.assemblies)
            raise Exception(
                "Multiple assemblies found: %s" % self.assemblies
            )
