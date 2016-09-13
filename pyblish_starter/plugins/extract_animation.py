import os
import datetime

from maya import cmds, mel
from pyblish import api


class ExtractStarterAnimation(api.InstancePlugin):
    """Produce an alembic of just point positions and normals.

    Positions and normals are preserved, but nothing more,
    for plain and predictable point caches.

    Limitations:
        - Framerange is bound to current maximum range in Maya

    """

    label = "Extract animation"
    order = api.ExtractorOrder
    hosts = ["maya"]
    families = ["starter.animation"]

    def process(self, instance):
        self.log.debug("Loading plug-in..")
        cmds.loadPlugin("AbcExport.mll", quiet=True)

        self.log.info("Extracting Alembic..")
        root = instance.context.data["workspaceDir"]
        time = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%SZ")
        dirname = os.path.join(root, "private", time, str(instance))
        filename = "%s.abc" % instance

        try:
            os.makedirs(dirname)
        except OSError:
            pass

        options = {
            "file": os.path.join(dirname, filename).replace("\\", "/"),
            "frameRange": "{startFrame} {endFrame}".format(
                startFrame=cmds.playbackOptions(query=True, ast=True),
                endFrame=cmds.playbackOptions(query=True, aet=True)),
            "uvWrite": "",  # Value-less flag
        }

        options.update(dict(("root", mesh) for mesh in instance))

        # Generate MEL command
        mel_args = list()
        for key, value in options.items():
            mel_args.append("-{0} {1}".format(key, value))

        mel_args_string = " ".join(mel_args)
        mel_cmd = "AbcExport -j \"{0}\"".format(mel_args_string)

        self.log.debug("Running MEL command: \"%s\"" % mel_cmd)
        mel.eval(mel_cmd)

        # Store reference for integration
        instance.data["privateDir"] = dirname

        self.log.info("Extracted {instance} to {dirname}".format(**locals()))
