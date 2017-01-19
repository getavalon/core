import pyblish.api


class ExtractMindbenderSource(pyblish.api.InstancePlugin):
    """Extract copy of working file at time of publish"""

    label = "Mindbender Source"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = [
        "mindbender.model",
        "mindbender.rig",
        "mindbender.animation",
    ]

    def process(self, instance):
        import os
        from maya import cmds
        from mindbender import api

        dirname = api.format_staging_dir(
            root=instance.context.data["workspaceDir"],
            time=instance.context.data["time"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "{name}.source".format(**instance.data)

        path = os.path.join(dirname, filename)

        # Perform extraction
        self.log.info("Performing extraction..")
        cmds.file(path,
                  force=True,
                  typ="mayaAscii",
                  exportAll=True,
                  defaultExtensions=False,
                  preserveReferences=False,
                  constructionHistory=True)

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {path}".format(**locals()))
