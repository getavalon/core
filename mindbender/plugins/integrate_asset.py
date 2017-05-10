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

        assert all(os.getenv(env) for env in (
            "MINDBENDER__ASSET", "MINDBENDER__PROJECT")), (
            "Missing environment variables\n"
            "This can sometimes happen when an application was launched \n"
            "manually, outside of the pipeline."
        )

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

        project = io.find_one({
            "_id": io.ObjectId(os.environ["MINDBENDER__PROJECT"])
        })

        asset = io.find_one({
            "_id": io.ObjectId(os.environ["MINDBENDER__ASSET"])
        })

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
            }
        }

        self.backwards_compatiblity(instance, version)

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
            "project": os.environ["MINDBENDER_PROJECT"],
            "silo": os.environ["MINDBENDER_SILO"],
            "asset": os.environ["MINDBENDER_ASSET"],
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
            if ext == ".json":
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
                }
            }

            io.insert_one(representation)

        self.log.info("Successfully integrated \"%s\" to \"%s\"" % (
            instance, dst))

    def backwards_compatiblity(self, instance, version):
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

        root = os.getenv("MINDBENDER_ASSETPATH")
        instancedir = os.path.join(root, "publish", instance.data["subset"])

        try:
            os.makedirs(instancedir)
        except OSError as e:
            if e.errno != errno.EEXIST:  # Already exists
                self.log.critical("An unexpected error occurred.")
                raise

        latest_version = api.find_latest_version(os.listdir(instancedir)) + 1
        versiondir = os.path.join(
            instancedir,
            api.format_version(latest_version)
        )

        try:
            with open(fname) as f:
                version_1_0 = json.load(f)

        except IOError:
            version_1_0 = dict(version, **{
                "schema": "mindbender-core:version-1.0",
                "path": os.path.join(
                    "{root}",
                    os.path.relpath(
                        versiondir,
                        os.path.join(
                            api.registered_root(),

                            # The meaning of "root" was changed
                            # in 2.0 to mean the root of all projects.
                            # Before, it was the root of one project,
                            # so we compensate by mimicking this behaviour.
                            os.environ["MINDBENDER_PROJECT"]
                        )
                    )
                ).replace("\\", "/").replace("f02_prod", ""),
                "representations": list(),

                "version": version["name"],

                # Used to identify family of assets already on disk
                "families": instance.data.get("families", list()) + [
                    instance.data.get("family")
                ],

                "time": context.data["time"],
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

        self.log.debug("Finished generating metadata: %s"
                       % json.dumps(version_1_0, indent=4))

        for filename in instance.data.get("files", list()):
            name, ext = os.path.splitext(filename)
            version_1_0["representations"].append(
                {
                    "schema": "mindbender-core:representation-1.0",
                    "format": ext,
                    "path": os.path.join(
                        "{dirname}",
                        "%s{format}" % name,
                    ).replace("\\", "/")
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
