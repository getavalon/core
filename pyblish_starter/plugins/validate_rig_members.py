from pyblish import api


class ValidateStarterRigMembers(api.InstancePlugin):
    """A rig must have certain members

    - controls_SEL
    - cache_SEL
    - resources_SEL (optional)

    """

    label = "Validate rig members"
    order = api.ValidatorOrder
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
