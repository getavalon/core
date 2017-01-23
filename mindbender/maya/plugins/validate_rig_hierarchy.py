import pyblish.api


class ValidateMindbenderRigHierarchy(pyblish.api.InstancePlugin):
    """A rig must reside under a single assembly called "ROOT"

    - Must reside within `ROOT` transform

    """

    label = "Validate Rig Hierarchy"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["mindbender.rig"]

    def process(self, instance):
        from maya import cmds

        assert cmds.ls(instance, assemblies=True) == ["ROOT"], (
            "Rig must have a single parent called 'ROOT'.")
