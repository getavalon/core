import os
from maya import cmds
from mindbender import api


class AnimationLoader(api.Loader):
    """Specific loader for animation

    This names the resulting container after the subset, rather than asset

    """

    families = ["mindbender.animation"]

    def process(self, fname, name, namespace):
        _, representation = os.path.splitext(fname)
        if representation == ".abc":
            cmds.loadPlugin("AbcImport.mll", quiet=True)

            nodes = cmds.file(
                fname,
                namespace=namespace,

                # Prevent identical alembic nodes
                # from being shared.
                sharedReferenceFile=False,

                groupReference=True,
                groupName=namespace + ":" + name,
                reference=True,
                returnNewNodes=True
            )

            return nodes

        self.log.warning("AnimationLoader: %s not supported yet."
                         % representation)

        return list()
