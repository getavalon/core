import pyblish.api


class MindbenderExtractHistoryLookdev(pyblish.api.InstancePlugin):
    """Export shaders for rendering

    Shaders are associated with an "mdID" attribute on each *transform* node.
    The extracted file is then given the name of the shader, and thereafter
    a relationship is created between a mesh and a file on disk.

    """

    label = "Extract History Lookdev"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = ["mindbender.historyLookdev"]

    def process(self, instance):
        import os
        import contextlib
        from maya import cmds
        from mindbender import api, maya

        @contextlib.contextmanager
        def sliced_connections():
            connections = list()

            try:
                # Slice connection from A -/> B
                for input_ in cmds.sets("in_SET", query=True) or list():
                    shape = cmds.listRelatives(input_, shapes=True)[0]
                    dst = shape + ".inMesh"

                    for src in cmds.listConnections(dst, plugs=True) or list():
                        pair = src, dst
                        cmds.disconnectAttr(*pair)
                        connections.append(pair)

                yield

            finally:
                # Restore connection
                for src, dst in connections:
                    cmds.connectAttr(src, dst, force=True)

        dirname = api.format_staging_dir(
            root=instance.context.data["workspaceDir"],
            time=instance.context.data["time"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        self.log.info("Extracting lookdev..")
        filename = "{name}.ma".format(**instance.data)
        path = os.path.join(dirname, filename)

        with (sliced_connections(),
              maya.maintained_selection(),
              maya.without_extension()):

            # Export
            cmds.select(instance, noExpand=True)

            cmds.file(
                path,
                force=True,
                type="mayaAscii",
                exportSelected=True,
                preserveReferences=False,
                constructionHistory=True,
            )

            # Store reference for integration
            if "files" not in instance.data:
                instance.data["files"] = list()

            instance.data["files"].append(filename)
            instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {path}".format(**locals()))
