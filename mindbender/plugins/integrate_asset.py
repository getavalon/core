import pyblish.api


class IntegrateMindbenderAsset(pyblish.api.InstancePlugin):
    """Write to files and metadata

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

    label = "Integrate Mindbender Asset"
    order = pyblish.api.IntegratorOrder
    families = [
        "mindbender.model",
        "mindbender.rig",
        "mindbender.animation",
        "mindbender.lookdev",
        "mindbender.historyLookdev",
    ]

    def process(self, instance):
        import os
        import errno
        import shutil
        from pprint import pformat

        from mindbender import api, io

        # Required environment variables
        MINDBENDER_PROJECT = os.environ["MINDBENDER_PROJECT"]
        MINDBENDER_ASSET = (
            instance.data.get("asset") or os.environ["MINDBENDER_ASSET"]
        )
        MINDBENDER_SILO = os.environ["MINDBENDER_SILO"]
        MINDBENDER_LOCATION = os.getenv("MINDBENDER_LOCATION")

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
        assert all(result["success"] for result in context.data["results"]), (
            "Atomicity not held, aborting.")

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

        self.log.debug("Establishing staging directory @ %s" % stagingdir)

        project = io.find_one({"type": "project"})
        asset = io.find_one({"name": MINDBENDER_ASSET})

        assert all([project, asset]), "This is bug"

        subset = io.find_one({
            "type": "subset",
            "parent": asset["_id"],
            "name": instance.data["subset"]
        })

        if subset is None:
            self.log.info("Subset '%s' not found, creating.."
                          % instance.data["subset"])

            _id = io.insert_one({
                "schema": "mindbender-core:subset-2.0",
                "type": "subset",
                "name": instance.data["subset"],
                "data": {},
                "parent": asset["_id"]
            }).inserted_id

            subset = io.find_one({"_id": _id})

        all_versions = [0] + [
            version["name"]
            for version in io.find({
                "type": "version",
                "parent": subset["_id"]
            }, {"name": True})
        ]

        next_version = sorted(all_versions)[-1] + 1

        # versiondir = template_versions.format(**template_data)
        self.log.debug("Next version: %i" % next_version)

        version = {
            "schema": "mindbender-core:version-2.0",
            "type": "version",
            "parent": subset["_id"],
            "name": next_version,

            # Imprint currently registered location
            "locations": list(
                location for location in
                [MINDBENDER_LOCATION]
                if location is not None
            ),

            "data": {
                # Used to identify family of assets already on disk
                "families": instance.data.get("families", list()) + [
                    instance.data.get("family")
                ],

                "time": context.data["time"],
                "author": context.data["user"],

                "source": os.path.join(
                    "{root}",
                    os.path.relpath(
                        context.data["currentFile"],
                        api.registered_root()
                    )
                ).replace("\\", "/"),

                "comment": context.data.get("comment"),
            }
        }

        self.backwards_compatiblity(instance, subset, version)

        self.log.debug("Creating version: %s" % pformat(version))
        version_id = io.insert_one(version).inserted_id

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
        template_data = {
            "root": api.registered_root(),
            "project": MINDBENDER_PROJECT,
            "silo": MINDBENDER_SILO,
            "asset": MINDBENDER_ASSET,
            "subset": subset["name"],
            "version": version["name"],
        }

        template_publish = project["config"]["template"]["publish"]

        for fname in os.listdir(stagingdir):
            name, ext = os.path.splitext(fname)
            template_data["representation"] = ext[1:]

            src = os.path.join(stagingdir, fname)
            dst = template_publish.format(**template_data)

            # Backwards compatibility
            if fname == ".metadata.json":
                dirname = os.path.dirname(dst)
                dst = os.path.join(dirname, ".metadata.json")

            self.log.info("Copying %s -> %s" % (src, dst))

            dirname = os.path.dirname(dst)
            try:
                os.makedirs(dirname)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    pass
                else:
                    self.log.critical("An unexpected error occurred.")
                    raise

            shutil.copy(src, dst)

            representation = {
                "schema": "mindbender-core:representation-2.0",
                "type": "representation",
                "parent": version_id,
                "name": ext[1:],
                "data": {
                    "label": {
                        ".ma": "Maya Ascii",
                        ".source": "Original source file",
                        ".abc": "Alembic"
                    }.get(ext)
                },

                # Imprint shortcut to context
                # for performance reasons.
                "context": {
                    "project": MINDBENDER_PROJECT,
                    "asset": MINDBENDER_ASSET,
                    "silo": MINDBENDER_SILO,
                    "subset": subset["name"],
                    "version": version["name"],
                    "representation": ext[1:]
                }
            }

            io.insert_one(representation)

        self.log.info("Successfully integrated \"%s\" to \"%s\"" % (
            instance, dst))

    def backwards_compatiblity(self, instance, subset, version):
        """Maintain backwards compatibility with newly published assets

        With the introduction of the database in 2.0, the artist would be
        unable to publish in 2.0 and use the files in 1.0. Therefore, we
        introduce this mechanism which continue to write for 1.0 even
        when writing from the 2.0 pipeline.

        This behaviour is deprecated and is to be removed in a future release.

        """

        import os
        import json
        import errno
        from mindbender import api

        MINDBENDER_PROJECT = os.environ["MINDBENDER_PROJECT"]
        MINDBENDER_ASSET = os.environ["MINDBENDER_ASSET"]
        MINDBENDER_SILO = os.environ["MINDBENDER_SILO"]

        context = instance.context

        # Metadata
        #  _________
        # |         |.key = value
        # |         |
        # |         |
        # |         |
        # |         |
        # |_________|
        #
        stagingdir = instance.data.get("stagingDir")
        fname = os.path.join(stagingdir, ".metadata.json")

        root = os.environ["MINDBENDER_ASSETPATH"]
        instancedir = os.path.join(root, "publish", instance.data["subset"])

        try:
            os.makedirs(instancedir)
        except OSError as e:
            if e.errno != errno.EEXIST:  # Already exists
                self.log.critical("An unexpected error occurred.")
                raise

        versiondir = os.path.join(
            instancedir,
            api.format_version(version["name"])
        )

        try:
            with open(fname) as f:
                version_1_0 = json.load(f)

        except IOError:
            version_1_0 = dict(version, **{
                "schema": "mindbender-core:version-1.0",

                # Hard-coded during transition
                "path": versiondir.replace("\\", "/"),
                "representations": list(),

                "version": version["name"],

                # Used to identify family of assets already on disk
                "families": instance.data.get("families", list()) + [
                    instance.data.get("family")
                ],

                "time": context.data["time"],
                "timeFormat": "%Y%m%dT%H%M%SZ",
                "author": context.data["user"],

                # Record within which silo this asset was made.
                "silo": os.environ["MINDBENDER_SILO"],

                # Collected by pyblish-maya
                "source": os.path.join(
                    "{root}",
                    os.path.relpath(
                        context.data["currentFile"],
                        os.path.join(
                            api.registered_root(),
                            os.environ["MINDBENDER_PROJECT"]
                        )
                    )
                ).replace("\\", "/"),

                # Discard database keys
                "parent": None,
            })

        for filename in instance.data.get("files", list()):
            name, ext = os.path.splitext(filename)
            version_1_0["representations"].append(
                {
                    "schema": "mindbender-core:representation-1.0",
                    "format": ext,
                    "path": os.path.join(
                        "{dirname}",
                        "%s{format}" % name,
                    ).replace("\\", "/"),

                    # Imprint shortcut to context
                    # for performance reasons.
                    "context": {
                        "project": MINDBENDER_PROJECT,
                        "asset": MINDBENDER_ASSET,
                        "silo": MINDBENDER_SILO,
                        "subset": subset["name"],
                        "version": version["name"],
                        "representation": ext[1:]
                    }
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
            json.dump(version_1_0, f, indent=4)

        self.log.info("Successfully wrote %s." % fname)
