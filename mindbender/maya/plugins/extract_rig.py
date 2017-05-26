import pyblish.api


class ExtractMindbenderRig(pyblish.api.InstancePlugin):
    """Produce Maya file compatible with referencing

    Rigs come in many flavours. This plug-in carefully only excludes
    nodes explicitly stated as excluded, bundles and resolves external
    references to the scene.

    """

    label = "Extract Mindbender Rig"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = ["mindbender.rig"]

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
            cmds.select(instance, noExpand=True)
            cmds.file(path,
                      force=True,
                      typ="mayaAscii",
                      exportSelected=True,
                      preserveReferences=False,
                      constructionHistory=True)

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {path}".format(**locals()))
