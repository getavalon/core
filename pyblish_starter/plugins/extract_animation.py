from pyblish import api


class ExtractStarterAnimation(api.InstancePlugin):
    """Produce an alembic of just point positions and normals.

    Positions and normals are preserved, but nothing more,
    for plain and predictable point caches.

    Limitations:
        - Framerange is bound to current maximum range in Maya

    """

    label = "Extract animation"
    order = api.ExtractorOrder
    hosts = ["maya"]
    families = ["starter.animation"]

    def process(self, instance):
        import os
        from maya import cmds
        from pyblish_starter import format_user_dir
        from pyblish_starter.maya import export_alembic

        self.log.debug("Loading plug-in..")
        cmds.loadPlugin("AbcExport.mll", quiet=True)

        self.log.info("Extracting animation..")
        dirname = format_user_dir(
            root=instance.context.data["workspaceDir"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "{name}.ma".format(**instance.data)

        export_alembic(
            nodes=instance,
            file=os.path.join(dirname, filename).replace("\\", "/"),
            frame_range=(cmds.playbackOptions(query=True, ast=True),
                         cmds.playbackOptions(query=True, aet=True)),
            uv_write=True
        )

        # Store reference for integration
        instance.data.update({
            "userDir": dirname,
            "filename": filename,
        })

        self.log.info("Extracted {instance} to {dirname}".format(**locals()))
