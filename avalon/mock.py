from avalon import api


class CreateModel(api.Creator):
    name = "MyModelDefault"
    label = "Model"
    family = "avalon.model"


class CreateRig(api.Creator):
    family = "avalon.rig"


class CreateAnimation(api.Creator):
    family = "avalon.animation"


creators = [
    CreateModel,
    CreateRig,
    CreateAnimation
]
