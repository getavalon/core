import pyblish.api


class ExtractMindbenderModel(pyblish.api.InstancePlugin):
    """Produce a stripped down Maya file from instance

    This plug-in takes into account only nodes relevant to models
    and discards anything else, especially deformers along with
    their intermediate nodes.

    """

    label = "Extract Mindbender Model"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = ["mindbender.model"]

    def process(self, instance):
        import os
        from maya import cmds
        from mindbender import api, maya

        dirname = api.format_staging_dir(
            root=instance.context.data["workspaceDir"],
            time=instance.context.data["time"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "{name}.ma".format(**instance.data)

        path = os.path.join(dirname, filename)

        # Perform extraction
        self.log.info("Performing extraction..")
        with maya.maintained_selection(), maya.without_extension():
            self.log.info("Extracting %s" % str(list(instance)))
            cmds.select(instance, noExpand=True)
            cmds.file(path,
                      force=True,
                      typ="mayaAscii",
                      exportSelected=True,
                      preserveReferences=False,

                      # Shader assignment is the responsibility of
                      # riggers, for animators, and lookdev, for rendering.
                      shader=False,

                      # Construction history inherited from collection
                      # This enables a selective export of nodes relevant
                      # to this particular plug-in.
                      constructionHistory=False)

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {path}".format(**locals()))
