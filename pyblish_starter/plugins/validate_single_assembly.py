import pyblish.api


class ValidateStarterSingleAssembly(pyblish.api.InstancePlugin):
    """Each asset must have a single top-level group"""

    label = "Single assembly"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["starter.model", "starter.rig"]

    def process(self, instance):
        from maya import cmds

        assemblies = cmds.ls(instance, assemblies=True)
        assert len(assemblies) == 1, (
            ("Multiple assemblies found."
                if len(assemblies) > 1
                else "No assembly found")
        )
