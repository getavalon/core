from pyblish import api


class ExtractStarterRig(api.InstancePlugin):
    """Produce Maya file compatible with referencing

    Rigs come in many flavours. This plug-in carefully only excludes
    nodes explicitly stated as excluded, bundles and resolves external
    references to the scene.

    Limits:
        - 1 rig per scene file

    """

    label = "Extract rig"
    order = api.ExtractorOrder
    hosts = ["maya"]
    families = ["starter.rig"]

    def process(self, instance):
        import os
        from maya import cmds
        from pyblish_starter import format_user_dir
        from pyblish_maya import maintained_selection

        dirname = format_user_dir(
            root=instance.context.data["workspaceDir"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "{name}.ma".format(**instance.data)

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
                      constructionHistory=True)

        # Store reference for integration
        instance.data.update({
            "userDir": dirname,
            "filename": filename,
        })

        self.log.info("Extracted {instance} to {path}".format(**locals()))
