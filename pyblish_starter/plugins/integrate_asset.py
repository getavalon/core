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

        userdir = instance.data.get("userDir")
        assert userdir, (
            "Incomplete instance \"%s\": "
            "Missing reference to user directory."
            % instance)

        root = instance.context.data["workspaceDir"]
        instancedir = os.path.join(root, "shared", str(instance))

        try:
            os.makedirs(instancedir)
        except OSError:
            pass

        version = len(os.listdir(instancedir)) + 1
        versiondir = os.path.join(
            instancedir,
            pyblish_starter.format_version(version)
        )

        shutil.copytree(userdir, versiondir)

        # Update metadata
        fname = os.path.join(versiondir, ".metadata.json")

        try:
            with open(fname) as f:
                metadata = json.load(f)
        except IOError:
            metadata = {
                "schema": "pyblish-starter:version-1.0",
                "version": version,
                "path": versiondir,
                "representations": list()
            }

        filename = instance.data["filename"]
        name, ext = os.path.splitext(filename)
        metadata["representations"].append(
            {
                "format": ext,
                "path": "{dirname}/%s{format}" % name
            }
        )

        with open(fname, "w") as f:
            json.dump(metadata, f, indent=4)

        self.log.info("Successfully integrated \"%s\" to \"%s\"" % (
            instance, versiondir))
