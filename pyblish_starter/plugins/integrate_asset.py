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
        import shutil

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

        versions = len(os.listdir(instancedir))
        next_version = "v%03d" % (versions + 1)
        versiondir = os.path.join(instancedir, next_version)

        shutil.copytree(privatedir, versiondir)

        self.log.info("Successfully integrated %s to %s" % (
            instance, versiondir))
