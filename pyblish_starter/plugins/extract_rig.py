from pyblish import api


class ExtractStarterRig(api.InstancePlugin):
    """Produce Maya file compatible with referencing
    
    Rigs come in many flavours. This plug-in carefully only excludes
    nodes explicitly stated as excluded, bundles and resolves external
    references to the scene.

    """

    label = "Extract rig"
    order = api.ExtractorOrder
    hosts = ["maya"]
    families = ["starter.rig"]

    def process(self, instance):
        pass
