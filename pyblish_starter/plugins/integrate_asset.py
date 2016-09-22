from pyblish import api


class IntegrateStarterAsset(api.InstancePlugin):
    """Publicise each instance

    Limitations:
        - Limited to publishing within a single Maya project

    """

    label = "Integrate asset"
    order = api.IntegratorOrder

    def process(self, instance):
        import os
        import json
        import shutil
        import pyblish_starter

        privatedir = instance.data.get("privateDir")
        assert privatedir, (
            "Incomplete instance \"%s\": "
            "Missing reference to private directory."
            % instance)

        root = instance.context.data["workspaceDir"]
        instancedir = os.path.join(root, "public", str(instance))

        try:
            os.makedirs(instancedir)
        except OSError:
            pass

        version = len(os.listdir(instancedir)) + 1
        versiondir = os.path.join(
            instancedir,
            pyblish_starter.format_version(version)
        )

        shutil.copytree(privatedir, versiondir)

        # Update metadata
        fname = os.path.join(versiondir, ".metadata.json")

        try:
            with open(fname) as f:
                metadata = json.load(f)
        except IOError:
            metadata = {
                "schema": "pyblish-starter:version-1.0",
                "version": version,
                "representations": list()
            }

        filename = instance.data["filename"]
        name, ext = os.path.splitext(filename)
        metadata["representations"].append(
            {
                "format": ext,
                "path": "{version}/%s" % filename
            }
        )

        with open(fname, "w") as f:
            json.dump(metadata, f)

        self.log.info("Successfully integrated \"%s\" to \"%s\"" % (
            instance, versiondir))
