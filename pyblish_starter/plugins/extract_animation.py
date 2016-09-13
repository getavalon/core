from pyblish import api


class ExtractStarterAnimation(api.InstancePlugin):
    """Produce an alembic of just point positions.
    
    Positions and normals are preserved, but nothing more.
    This keeps caches plain and predictable.

    """

    label = "Extract animation"
    order = api.ExtractorOrder
    hosts = ["maya"]
    families = ["starter.animation"]

    def process(self, instance):
        pass
