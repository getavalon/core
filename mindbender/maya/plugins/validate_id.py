import pyblish.api


class ValidateMindbenderID(pyblish.api.InstancePlugin):
    """All models must have an ID attribute"""

    label = "Validate Mindbender ID"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = [
        "mindbender.model",
        "mindbender.lookdev",
    ]

    def process(self, instance):
        from maya import cmds

        nodes = list(instance)
        nodes += cmds.listRelatives(instance, allDescendents=True) or list()
        missing = list()

        for node in nodes:

            # Only check transforms with shapes that are meshes
            if not cmds.nodeType(node) == "transform":
                continue

            shapes = cmds.listRelatives(node, shapes=True, type="mesh") or list()
            meshes = cmds.ls(shapes, type="mesh")

            if not meshes:
                continue

            try:
                self.log.info("Checking '%s'" % node)
                cmds.getAttr(node + ".mbID")
            except ValueError:
                missing.append(node)

        assert not missing, ("Missing ID attribute on: %s"
                             % ", ".join(missing))
