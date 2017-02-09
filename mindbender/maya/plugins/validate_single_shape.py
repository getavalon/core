import pyblish.api


class ValidateMindbenderSingleShape(pyblish.api.InstancePlugin):
    """Transforms with a mesh must ever only contain a single mesh

    This ensures models only contain a single shape node.

    """

    label = "Validate Single Shape"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = [
        "mindbender.model",
    ]

    def process(self, instance):
        from maya import cmds

        has_multiple_shapes = list()

        # Consider entire hierarchy of nodes included in an Instance
        hierarchy = cmds.listRelatives(instance, allDescendents=True)

        # Consider only nodes of type="mesh"
        meshes = cmds.ls(hierarchy, type="mesh", long=True)
        transforms = cmds.listRelatives(meshes, parent=True)

        for transform in set(transforms):
            shapes = cmds.listRelatives(transform, shapes=True) or list()

            # Ensure the one child is a shape
            has_single_shape = len(shapes) == 1
            self.log.info("has single shape: %s" % has_single_shape)

            # Ensure the one shape is of type "mesh"
            has_single_mesh = (
                has_single_shape and
                cmds.nodeType(shapes[0]) == "mesh"
            )
            self.log.info("has single mesh: %s" % has_single_mesh)

            if not all([has_single_shape, has_single_mesh]):
                has_multiple_shapes.append(transform)

        assert not has_multiple_shapes, (
            "\"%s\" has transforms with multiple shapes: %s" % (
                instance, ", ".join(
                    "\"" + member + "\"" for member in has_multiple_shapes))
        )
