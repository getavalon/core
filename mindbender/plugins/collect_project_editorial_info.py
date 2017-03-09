# collect_project_editorial_info.py
import pyblish.api


class CollectMindbenderEditInfo(pyblish.api.ContextPlugin):
    """Store projects editorial info at the time of publish"""

    label = "Collect Project Edit Info"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    families = [
        "mindbender.animation"
    ]

    def process(self, context):
        import os

        for env in os.environ:
            if "MINDBENDER" in env:
                if "FPS" in env:
                    mindbender_fps = env
                if "EDIT_IN" in env:
                    mindbender_edit_in = env
                if "EDIT_OUT" in env:
                    mindbender_edit_out = env

        if mindbender_fps == "" or mindbender_fps is None:
            context.data["projectFPS"] = 25
        elif mindbender_fps is not None:
            context.data["projectFPS"] = int(mindbender_fps)

        if mindbender_edit_in == "" or mindbender_edit_in is None:
            context.data["projectEditIn"] = 101
        elif mindbender_edit_in is not None:
            context.data["projectEditIn"] = int(mindbender_edit_in)

        if mindbender_edit_out == "" or mindbender_edit_out is None:
            context.data["projectEditOut"] = 201
        elif mindbender_edit_out is not None:
            context.data["projectEditOut"] = int(mindbender_edit_out)
