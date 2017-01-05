import pyblish.api


class CollectMindbenderTime(pyblish.api.ContextPlugin):
    """Store global time at the time of publish"""

    label = "Mindbender Time"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]

    def process(self, context):
        from mindbender import api
        context.data["time"] = api.time()
