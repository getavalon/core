from pyblish import api


class ValidateStarterRigHierarchy(api.InstancePlugin):
    """A rig must reside under a single assembly called "rig_GRP"

    - Must reside within `rig_GRP` transform

    """

    label = "Validate rig hierarchy"
    order = api.ValidatorOrder
    hosts = ["maya"]
    families = ["starter.rig"]

    def process(self, instance):
        from maya import cmds

        assert cmds.ls(instance, assemblies=True) == ["model_GRP"], (
            "Rig must have a single parent called 'model_GRP'.")
