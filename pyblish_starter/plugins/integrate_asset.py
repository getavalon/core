import pyblish.api


class IntegrateStarterAsset(pyblish.api.InstancePlugin):
    """Move user data to shared location

    This plug-in exposes your data to others by encapsulating it
    into a new version.

    Schema:
        Data is written in the following format.
         ____________________
        |                    |
        | version            |
        |  ________________  |
        | |                | |
        | | representation | |
        | |________________| |
        | |                | |
        | | ...            | |
        | |________________| |
        |____________________|

    """

    label = "Starter Asset"
    order = pyblish.api.IntegratorOrder
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
        from pyblish_starter import api

        context = instance.context

        # Atomicity
        #
        # Guarantee atomic publishes - each asset contains
        # an identical set of members.
        #     __
        #    /     o
        #   /       \
        #  |    o    |
        #   \       /
        #    o   __/
        #
        if not all(result["success"] for result in context.data["results"]):
            raise Exception("Atomicity not held, aborting.")

        # Assemble
        #
        #       |
        #       v
        #  --->   <----
        #       ^
        #       |
        #
        stagingdir = instance.data.get("stagingDir")
        assert stagingdir, (
            "Incomplete instance \"%s\": "
            "Missing reference to staging area."
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

        version = api.find_latest_version(os.listdir(instancedir)) + 1
        versiondir = os.path.join(instancedir, api.format_version(version))

        # Metadata
        #  _________
        # |         |.key = value
        # |         |
        # |         |
        # |         |
        # |         |
        # |_________|
        #
        fname = os.path.join(stagingdir, ".metadata.json")

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
                "source": os.path.join(
                    "{root}",
                    os.path.relpath(
                        context.data["currentFile"],
                        api.root()
                    )
                ),
            }

        for filename in instance.data.get("files", list()):
            name, ext = os.path.splitext(filename)
            metadata["representations"].append(
                {
                    "schema": "pyblish-starter:representation-1.0",
                    "format": ext,
                    "path": "{dirname}/%s{format}" % name
                }
            )

        # Write to disk
        #          _
        #         | |
        #        _| |_
        #    ____\   /
        #   |\    \ / \
        #   \ \    v   \
        #    \ \________.
        #     \|________|
        #
        with open(fname, "w") as f:
            json.dump(metadata, f, indent=4)

        # Metadata is written before being validated -
        # this way, if validation fails, the data can be
        # inspected by hand from within the user directory.
        api.schema.validate(metadata, "version")
        shutil.copytree(stagingdir, versiondir)

        self.log.info("Successfully integrated \"%s\" to \"%s\"" % (
            instance, versiondir))
