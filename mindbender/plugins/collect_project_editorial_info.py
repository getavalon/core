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

        if "environment" not in context.data:
            context.data["environment"] = dict()

        prefix = "MINDBENDER_"
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            key = key[len(prefix):]

            # Convert EDIT_IN to EditIn, FPS to Fps.
            key = "".join(k.title() for k in key.split("_"))

            # Decorate key with "mindbender" to match prev namning convention
            decoration = prefix.replace("_", "")
            decoration = decoration.lower()
            key = decoration + key

            context.data["environment"][key] = value
