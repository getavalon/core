from avalon import api, blender


def register():
    """Register Avalon with Blender."""
    print("Registering Avalon...")
    api.install(blender)
