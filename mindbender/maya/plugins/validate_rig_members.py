import pyblish.api


class ValidateMindbenderRigFormat(pyblish.api.InstancePlugin):
    """A rig must have a certain hierarchy and members

    - Must reside within `rig_GRP` transform
    - out_SET
    - controls_SET
    - in_SET (optional)
    - resources_SET (optional)

    """

    label = "Validate Rig Format"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["mindbender.rig"]

    def process(self, instance):
        from maya import cmds

        missing = list()

        for member in ("controls_SET",
                       "out_SET"):
            if member not in instance:
                missing.append(member)

        assert not missing, "\"%s\" is missing members: %s" % (
            instance, ", ".join("\"" + member + "\"" for member in missing))

        # Ensure all output has IDs.
        # As user may inadvertently add to the out_SET without
        # realising, and some of the new members may be non-meshes,
        # or meshes without and ID
        missing = list()

        for node in cmds.sets("out_SET", query=True) or list():

            # Only check transforms with shapes that are meshes
            shapes = cmds.listRelatives(node, shapes=True) or list()
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
