import pyblish.api


class ValidateStarterModelHierarchy(pyblish.api.InstancePlugin):
    """A model hierarchy must reside under a single assembly called "model_GRP"

    - Must reside within `model_GRP` transform

    """

    label = "Model Format"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["starter.model"]

    def process(self, instance):
        from maya import cmds

        assert cmds.ls(instance, assemblies=True) == ["model_GRP"], (
            "Model must have a single parent called 'model_GRP'.")
