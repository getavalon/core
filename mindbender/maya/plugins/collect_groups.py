import pyblish.api


class CollectMindbenderGroups(pyblish.api.ContextPlugin):
    order = pyblish.api.CollectorOrder
    active = False

    def process(self, context):
        instance = context.create_instance("heroGroup")
        instance.data["family"] = "mindbender.group"
        instance.data["subset"] = instance.name
        instance.data.update({
            "members": {
                "geometry": [
                    "hero:modelDefault.ma",
                    "hero:modelLow.ma",
                    "hero:rigDefault.ma",
                    "shot1:hero01.curves",
                    "shot1:hero01.abc"
                ],
                "shader": [
                    "hero:lookdevDefault.ma",
                    "hero:lookdevAnimation.ma"
                ]
            },
            "presets": {
                "animation": {
                    "geometry": "shot1:hero01.curves",
                    "shader": "hero:lookdevAnimation.ma"
                },
                "rendering": {
                    "geometry": "shot1:hero01.abc",
                    "shader": "hero:lookdevDefault.ma"
                },
                "layout": {
                    "geometry": "hero:rigDefault.ma",
                    "shader": "hero:lookdevAnimation.ma"
                }
            }
        })
