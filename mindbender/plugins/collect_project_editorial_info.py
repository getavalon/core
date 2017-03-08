# collect_project_editorial_info.py
import pyblish.api


class CollectMindbenderEditInfo(pyblish.api.ContextPlugin):
    """Store projects editorial info at the time of publish"""

    label = "Collect Project Edit Info"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    families = [
        # More will come
        "mindbender.animation"
    ]

    def process(self, context):
        import os

        mindbender_fps = os.getenv("MINDBENDER_FPS")
        mindbender_edit_in = os.getenv("MINDBENDER_EDIT_IN")
        mindbender_edit_out = os.getenv("MINDBENDER_EDIT_OUT")

        if mindbender_fps == "" or mindbender_fps is None:
            context.data["project_fps"] = 25
        elif mindbender_fps is not None:
            context.data["project_fps"] = int(mindbender_fps)

        if mindbender_edit_in == "" or mindbender_edit_in is None:
            context.data["project_edit_in"] = 101
        elif mindbender_edit_in is not None:
            context.data["project_edit_in"] = int(mindbender_edit_in)

        if mindbender_edit_out == "" or mindbender_edit_out is None:
            context.data["project_edit_out"] = 201
        elif mindbender_edit_out is not None:
            context.data["project_edit_out"] = int(mindbender_edit_out)
