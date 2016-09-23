from pyblish import api


class ValidateStarterResources(api.InstancePlugin):
    """Resources must not contain absolute paths.

    When working with external files, such as textures and references,
    it's important to ensure that the published content is able to
    reference these paths without relying on the environment at the
    time of publish.

    """

    label = "Validate resources"
    order = api.ValidatorOrder
    hosts = ["maya"]
    families = ["starter.model", "starter.rig"]

    def process(self, instance):
        import os
        from maya import cmds

        if "resources_SEL" not in instance:
            return

        absolute = dict()
        for resource in cmds.sets("resources_SEL", query=True):
            if cmds.nodeType(resource) == "reference":
                filename = cmds.referenceQuery(resource,
                                               filename=True,
                                               unresolvedName=True)
                if os.path.isabs(filename):
                    absolute[resource] = filename

        assert not absolute, (
            "Some resources were absolute: " +
            ", ".join(absolute)
        )
