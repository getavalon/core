import pyblish.api


class ValidateStarterRigFormat(pyblish.api.InstancePlugin):
    """A rig must have a certain hierarchy and members

    - Must reside within `rig_GRP` transform
    - controls_SEL
    - cache_SEL
    - resources_SEL (optional)

    """

    label = "Rig Format"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["starter.rig"]

    def process(self, instance):
        missing = list()

        for member in ("controls_SEL",
                       "cache_SEL"):
            if member not in instance:
                missing.append(member)

        assert not missing, "\"%s\" is missing members: %s" % (
            instance, ", ".join("\"" + member + "\"" for member in missing))
