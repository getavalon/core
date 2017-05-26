import pyblish.api


class ExtractMindbenderCurves(pyblish.api.InstancePlugin):
    label = "Extract Mindbender Curves"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = ["mindbender.animation"]

    def process(self, instance):
        import os
        from maya import cmds
        from mindbender import api, maya

        self.log.debug("Loading plug-in..")
        cmds.loadPlugin("atomImportExport.mll", quiet=True)

        self.log.info("Extracting curves..")
        dirname = api.format_staging_dir(
            root=instance.context.data["workspaceDir"],
            time=instance.context.data["time"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "{name}.curves".format(**instance.data)

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

        controls = next((
            node for node in instance
            if node.endswith("controls_SET")),
            None
        )

        if controls is None:
            # Backwards compatibility
            self.log.warning("%s is missing a controls_SET" % instance.name)
            return

        with maya.maintained_selection(), maya.without_extension():
            cmds.select(controls, noExpand=False)
            cmds.file(
                os.path.join(dirname, filename).replace("\\", "/"),
                force=True,
                options=options,
                typ="atomExport",
                exportSelected=True
            )

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {dirname}".format(**locals()))
