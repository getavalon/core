import pyblish.api


class ExtractMindbenderHistory(pyblish.api.InstancePlugin):
    label = "Extract Mindbender History"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = ["mindbender.animation"]

    def process(self, instance):
        import os
        from maya import cmds
        from mindbender import api, maya

        self.log.info("Extracting history..")

        dirname = api.format_staging_dir(
            root=instance.context.data["workspaceDir"],
            time=instance.context.data["time"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "{name}.history".format(**instance.data)

        options = ";".join([
            "precision=8",
            "statics=1",
            "baked=1",
            "sdk=0",
            "constraint=0",
            "animLayers=0",
            "selected=selectedOnly",
            "whichRange=1",
            "range=1:10",
            "hierarchy=none",
            "controlPoints=0",
            "useChannelBox=1",
            "options=keys",
            ("copyKeyCmd="
                "-animation objects "
                "-option keys "
                "-hierarchy none "
                "-controlPoints 0 ")
        ])

        with maya.maintained_selection(), maya.without_extension():
            cmds.select(instance, noExpand=True)
            cmds.exportEdits(
                os.path.join(dirname, filename).replace("\\", "/"),
                force=True,
                type="editMA",
                selected=True,
                includeNetwork=True,
                includeAnimation=True,
                includeSetAttrs=True,
            )

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {dirname}".format(**locals()))
