from mindbender import api


class CreateModel(api.Creator):
    name = "MyModelDefault"
    label = "Model"
    family = "mindbender.model"


class CreateRig(api.Creator):
    family = "mindbender.rig"


class CreateAnimation(api.Creator):
    family = "mindbender.animation"


creators = [
    CreateModel,
    CreateRig,
    CreateAnimation
]
