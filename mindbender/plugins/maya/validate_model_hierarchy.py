import pyblish.api


class ValidateMindbenderModelHierarchy(pyblish.api.InstancePlugin):
    """A model hierarchy must reside under a single assembly called "ROOT"

    - Must reside within `ROOT` transform

    """

    label = "Validate Model Format"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["mindbender.model"]

    def process(self, instance):
        from maya import cmds

        assert cmds.ls(instance, assemblies=True) == ["ROOT"], (
            "Model must have a single parent called 'ROOT'.")
