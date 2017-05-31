from mindbender import maya


class GroupLoader(maya.Loader):
    """Specific loader of Alembic for the mindbender.animation family"""

    families = ["mindbender.group"]
    representations = ["group"]

    def process(self, name, namespace, context):
        import os
        import json
        from maya import cmds
        from mindbender import maya, io

        with open(self.fname) as f:
            group = json.load(f)

        preset = group["presets"][context["preset"]]
        all_assemblies = list()
        all_nodes = list()

        project = os.environ["MINDBENDER_PROJECT"]
        for slot, pointer in preset.items():
            asset, pointer = pointer.split(":", 1)
            subset, representation = pointer.rsplit(".", 1)

            representation = io.locate([
                project,
                asset,
                subset,
                -1,
                representation
            ])

            # A group should have been validated before it was created,
            # and representations are immutable and permanent.
            assert representation is not None, "This is a bug"

            container = maya.load(representation)
            nodes = cmds.sets(container, query=True) or []
            assemblies = cmds.ls(nodes, assemblies=True) or []

            all_assemblies.extend(assemblies)
            all_nodes.extend(nodes)

        self.assemblies = all_assemblies
        self[:] = all_nodes

        return all_nodes

    def post_process(self, name, namespace, context):
        from maya import cmds

        if self.assemblies:
            self.append(cmds.group(self.assemblies, name=name))
