import pyblish.api


class ValidateMindbenderRigFormat(pyblish.api.InstancePlugin):
    """A rig must have a certain hierarchy and members

    - Must reside within `rig_GRP` transform
    - out_SET
    - controls_SET
    - in_SET (optional)
    - resources_SET (optional)

    """

    label = "Rig Format"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["mindbender.rig"]

    def process(self, instance):
        missing = list()

        for member in ("controls_SET",
                       "out_SET"):
            if member not in instance:
                missing.append(member)

        assert not missing, "\"%s\" is missing members: %s" % (
            instance, ", ".join("\"" + member + "\"" for member in missing))
