import pyblish.api


class ExtractMindbenderAnimation(pyblish.api.InstancePlugin):
    """Produce an alembic of just point positions and normals.

    Positions and normals are preserved, but nothing more,
    for plain and predictable point caches.

    Limitations:
        - Framerange is bound to current maximum range in Maya

    """

    label = "Extract Mindbender Animation"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = ["mindbender.animation"]

    def process(self, instance):
        import os
        from maya import cmds
        from mindbender import api, maya

        self.log.debug("Loading plug-in..")
        cmds.loadPlugin("AbcExport.mll", quiet=True)

        self.log.info("Extracting animation..")
        dirname = api.format_staging_dir(
            root=instance.context.data["workspaceDir"],
            time=instance.context.data["time"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "{name}.abc".format(**instance.data)

        maya.export_alembic(
            nodes=instance,
            file=os.path.join(dirname, filename).replace("\\", "/"),

            frame_range=(instance.data["startFrame"],
                         instance.data["endFrame"]),

            # Include UVs
            uv_write=True,

            # Include all attributes prefixed with this
            attribute_prefix="mb"
        )

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {dirname}".format(**locals()))
