from pyblish import api


class IntegrateStarterAsset(api.ContextPlugin):
    label = "Integrate asset"
    order = api.IntegratorOrder

    def process(self, context):
        import os
        import shutil

        root = context.data["workspaceDir"]
        dirname = os.path.join(root, "public")

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        versions = len(os.listdir(dirname))
        next_version = "v%03d" % (versions + 1)
        versiondir = os.path.join(dirname, next_version)

        atomic = True

        for instance in context:
            privatedir = instance.data.get("privateDir")

            if not privatedir:
                self.log.warning("Incomplete extraction of \"%s\", "
                                 "missing reference to private directory"
                                 % instance)
                atomic = False
                continue



            shutil.copytree(privatedir, versiondir)

            self.log.info("Successfully integrated %s" % instance)

        # Indicate that this integration was complete - i.e. atomic.
        assert atomic, "Integration incomplete."

        atomicname = os.path.join(versiondir, ".complete")
        open(atomicname, "a").close()

        self.log.info("Integration completed successfully.")
