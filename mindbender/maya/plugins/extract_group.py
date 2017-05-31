import pyblish.api


class ExtractMindbenderGroup(pyblish.api.InstancePlugin):
    label = "Extract Mindbender Group"
    order = pyblish.api.ExtractorOrder
    hosts = ["maya"]
    families = ["mindbender.group"]

    def process(self, instance):
        import os
        import json
        from mindbender import api

        self.log.info("Extracting group..")
        dirname = api.format_staging_dir(
            root=instance.context.data["workspaceDir"],
            time=instance.context.data["time"],
            name=instance.data["name"])

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        filename = "{name}.group".format(**instance.data)

        with open(os.path.join(dirname, filename), "w") as f:
            json.dump({
                key: instance.data.get(key)
                for key in ("name", "members", "presets")
            }, f)

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)
        instance.data["stagingDir"] = dirname

        self.log.info("Extracted {instance} to {dirname}".format(**locals()))
