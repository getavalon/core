import pyblish.api


class CollectStarterInstances(pyblish.api.ContextPlugin):
    """Gather instances by objectSet and pre-defined attribute

    This collector takes into account assets that are associated with
    an objectSet and marked with a unique identifier;

    Identifier:
        id (str): "pyblish.starter.instance"

    Supported Families:
        starter.model: Geometric representation of artwork
        starter.rig: An articulated model for animators.
            A rig may contain a series of sets in which to identify
            its contents.

            - cache_SEL: Should contain cachable polygonal meshes
            - controls_SEL: Should contain animatable controllers for animators
            - resources_SEL: Should contain nodes that reference external files

            Limitations:
                - Only Maya is supported
                - One (1) rig per scene file
                - Unmanaged history, it is up to the TD to ensure
                    history is up to par.
        starter.animation: Pointcache of `starter.rig`

    Limitations:
        - Does not take into account nodes connected to those
            within an objectSet. Extractors are assumed to export
            with history preserved, but this limits what they will
            be able to achieve and the amount of data available
            to validators.

    """

    label = "Starter Instances"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        try:
            # Assertion also made in pyblish_starter.install()
            # but as plug-ins can be used vanilla, the check
            # must also be made here.
            import pyblish_maya
            assert pyblish_maya.is_setup()

        except (ImportError, AssertionError):
            raise RuntimeError("pyblish-starter requires pyblish-maya "
                               "to have been setup.")

        for objset in cmds.ls("*.id",
                              long=True,            # Produce full names
                              type="objectSet",     # Only consider objectSets
                              recursive=True,       # Include namespace
                              objectsOnly=True):    # Return objectSet, rather
                                                    # than its members

            if not cmds.objExists(objset + ".id"):
                continue

            if not cmds.getAttr(objset + ".id") == "pyblish.starter.instance":
                continue

            # The developer is responsible for specifying
            # the family of each instance.
            assert cmds.objExists(objset + ".family"), (
                "\"%s\" was missing a family" % objset)

            name = cmds.ls(objset, long=False)[0]  # Use short name
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
                    value = None

                instance.data[attr] = value

            # Produce diagnostic message for any graphical
            # user interface interested in visualising it.
            self.log.info("Found: \"%s\" " % instance.data["name"])
