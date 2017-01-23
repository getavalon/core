import pyblish.api


class ValidateMindbenderSingleShape(pyblish.api.InstancePlugin):
    """One mesh per transform"""

    label = "Validate Single Shape"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    active = False
    optional = True
    families = [
        "mindbender.model",
        "mindbender.lookdev"
    ]

    def process(self, instance):
        from maya import cmds

        has_multiple_shapes = list()
        for node in instance:

            children = cmds.listRelatives(node, allDescendents=True) or list()
            shapes = cmds.listRelatives(node, shapes=True) or list()

            # Ensure there is only one child; there could be many,
            # including other transform nodes.
            has_single_shape = len(children) == 1

            # Ensure the one child is a shape
            has_single_child = len(shapes) == 1

            # Ensure the one child is of type "mesh"
            has_single_mesh = cmds.nodeType(shapes[0]) == "mesh"

            if not all([has_single_child,
                        has_single_shape,
                        has_single_mesh]):
                has_multiple_shapes.append(node)

        assert not has_multiple_shapes, (
            "\"%s\" has transforms with multiple shapes: %s" % (
                instance, ", ".join(
                    "\"" + member + "\"" for member in has_multiple_shapes))
        )
