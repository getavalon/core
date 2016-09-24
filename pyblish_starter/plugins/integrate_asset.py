from pyblish import api


class IntegrateStarterAsset(api.InstancePlugin):
    """Move user data to shared location

    This plug-in exposes your data to others by encapsulating it
    into a new version.

    """

    label = "Integrate asset"
    order = api.IntegratorOrder
    families = [
        "starter.model",
        "starter.rig",
        "starter.animation"
    ]

    def process(self, instance):
        import os
        import json
        import errno
        import shutil
        from pyblish_starter import (
            format_version,
            find_latest_version,
        )

        context = instance.context

        userdir = instance.data.get("userDir")
        assert userdir, (
            "Incomplete instance \"%s\": "
            "Missing reference to user directory."
            % instance
        )

        root = context.data["workspaceDir"]
        instancedir = os.path.join(root, "shared", instance.data["name"])

        try:
            os.makedirs(instancedir)
        except OSError as e:
            if e.errno != errno.EEXIST:  # Already exists
                self.log.critical("An unexpected error occurred.")
                raise

        version = find_latest_version(os.listdir(instancedir)) + 1
        versiondir = os.path.join(
            instancedir,
            format_version(version)
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
                "representations": list(),

                # Collected by pyblish-base
                "time": context.data["date"],
                "author": context.data["user"],

                # Collected by pyblish-maya
                "source": context.data["currentFile"],
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
