from pyblish import api


class CollectStarterInstances(api.ContextPlugin):
    """Gather instances by objectSet and pre-defined attribute

    This collector takes into account assets that are associated with
    an objectSet and marked with a unique identifier;

    Identifier:
        id (str): "pyblish.starter.instance"

    """

    label = "Collect instances"
    order = api.CollectorOrder
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        try:
            import pyblish_maya
            assert pyblish_maya.was_setup()

        except (ImportError, AssertionError):
            raise RuntimeError("pyblish-starter requires pyblish-maya "
                               "to have been setup.")

        for objset in cmds.ls("*.id",
                              long=True,          # Produce full names
                              type="objectSet",   # Only consider objectSets
                              recursive=True,     # Include namespace
                              objectsOnly=True):  # Return objectSet, rather
                                                  # than its members

            if not cmds.objExists(objset + ".id"):
                continue

            if not cmds.getAttr(objset + ".id") == "pyblish.starter.instance":
                continue

            # The developer is responsible for specifying
            # the family of each instance.
            assert cmds.objExists(objset + ".family"), (
                "\"%s\" was missing a family" % objset)

            name = cmds.ls(objset, long=False)[0]  # Use short name for instances
            instance = context.create_instance(name)
            instance[:] = cmds.sets(objset, query=True) or list()

            # Apply each user defined attribute as data
            for attr in cmds.listAttr(objset, userDefined=True) or list():
                try:
                    value = cmds.getAttr(objset + "." + attr)
                except:
                    # Some attributes cannot be read directly,
                    # such as mesh and color attributes. These
                    # are considered non-essential to this
                    # particular publishing pipeline.
                    continue

                instance.data[attr] = value
            
            # Produce diagnostic message for any graphical
            # user interface interested in visualising it.
            self.log.info("Found: %s " % objset)
