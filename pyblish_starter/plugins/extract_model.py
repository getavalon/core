from pyblish import api
import pyblish_starter as starter


class ExtractStarterModel(api.InstancePlugin):
    """Produce a stripped down Maya file from instance

    This plug-in takes into account only nodes relevant to models
    and discards anything else, especially deformers along with
    their intermediate nodes.

    """

    label = "Extract starter model"
    order = api.ExtractorOrder
    hosts = ["maya"]
    families = ["starter.model"]

    def process(self, instance):
        import os
        from maya import cmds
        from pyblish_maya import maintained_selection

        dirname = starter.format_user_dir(
            root=instance.context.data["workspaceDir"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "%s.ma" % instance

        path = os.path.join(dirname, filename)

        # Perform extraction
        self.log.info("Performing extraction..")
        with maintained_selection():
            cmds.select(instance, noExpand=True)
            cmds.file(path,
                      force=True,
                      typ="mayaAscii",
                      exportSelected=True,
                      preserveReferences=False,
                      constructionHistory=False)

        # Store reference for integration
        instance.data["userDir"] = dirname
        instance.data["filename"] = filename

        self.log.info("Extracted {instance} to {path}".format(**locals()))
