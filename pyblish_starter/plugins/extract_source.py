import pyblish.api


class ExtractStarterSource(pyblish.api.InstancePlugin):
    """Extract copy of working file at time of publish"""

    label = "Starter Source"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = [
        "starter.model",
        "starter.rig",
        "starter.animation",
    ]

    def process(self, instance):
        import os
        from maya import cmds
        from pyblish_starter import api

        dirname = api.format_staging_dir(
            root=instance.context.data["workspaceDir"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "source.ma"

        path = os.path.join(dirname, filename)

        # Perform extraction
        self.log.info("Performing extraction..")
        cmds.file(path,
                  force=True,
                  typ="mayaAscii",
                  exportAll=True,
                  preserveReferences=False,
                  constructionHistory=True)

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {path}".format(**locals()))
