from pyblish import api


class ValidateStarterSingleAssembly(api.InstancePlugin):
    """A rig must have a certain hierarchy and members

    - Must reside within `rig_GRP` transform
    - controls_SEL
    - cache_SEL
    - resources_SEL (optional)

    """

    label = "Validate single assembly"
    order = api.ValidatorOrder
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
