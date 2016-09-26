import pyblish.api


class ValidateStarterEncapsulation(pyblish.api.InstancePlugin):
    """Resources must not contain absolute paths.

    When working with external files, such as textures and caches,
    it's important to ensure that the published content is able to
    reference these paths without relying on the environment at the
    time of publish.

    """

    label = "Encapsulation"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["starter.model", "starter.rig"]

    def process(self, instance):
        import os
        from maya import cmds

        # Resources are optional
        if "resources_SEL" not in instance:
            return

        resources = dict()
        for resource in cmds.sets("resources_SEL", query=True):
            if cmds.nodeType(resource) == "reference":
                path = cmds.referenceQuery(resource,
                                           filename=True,
                                           unresolvedName=True)

            elif cmds.nodeType(resource) == "AlembicNode":
                path = cmds.getAttr(resource + ".abc_File")

            else:
                # Unsupported
                path = None

            resources[resource] = path

        # All resources were resolved
        assert all(resources.values()), (
            "Unsupported resource(s): " +
            ", ".join("'%s': '%s'" % (resource, path)
                      for resource, path in resources.items()
                      if path is not None)
        )

        # No resource contains an absolute path
        assert not any(os.path.isabs(fname) for fname in resources), (
            "Some resources are absolute: " +
            ", ".join(resources)
        )
