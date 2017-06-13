from mindbender import maya


class CreateAnimation(maya.Creator):
    """Any character or prop animation"""

    name = "animationDefault"
    family = "mindbender.animation"
    label = "Animation"

    def __init__(self, *args, **kwargs):
        super(CreateAnimation, self).__init__(*args, **kwargs)
        from maya import cmds

        self.data.update({
            "startFrame": lambda: cmds.playbackOptions(
                query=True, animationStartTime=True),
            "endFrame": lambda: cmds.playbackOptions(
                query=True, animationEndTime=True),
        })
