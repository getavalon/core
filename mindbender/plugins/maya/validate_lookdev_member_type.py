import pyblish.api


class ValidateMindbenderLookdevMembers(pyblish.api.InstancePlugin):
    """A lookdev instance must only contain members of type 'transform'"""

    label = "Validate Lookdev Member Types"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["mindbender.lookdev"]

    def process(self, instance):
        from maya import cmds

        has_wrong_type = list(
            node for node in instance
            if cmds.nodeType(node) != "transform"
        )

        assert not has_wrong_type, "\"%s\" is has_wrong_type members: %s" % (
            instance, ", ".join("\"" + member + "\""
                                for member in has_wrong_type))
