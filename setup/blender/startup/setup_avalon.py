from avalon import api, blender


def register():
    """Register Avalon with Blender."""

    print("Registering Avalon...")
    api.install(blender)

    # Uncomment the following lines if you temporarily need to prevent Blender
    # from crashing due to errors in Qt related code. Note however that this
    # can be dangerous and have unwanted complications. The excepthook may
    # already be overridden (with good reason) and this will remove the
    # previous override.
    # import sys
    # sys.excepthook = lambda *exc_info: traceback.print_exception(*exc_info)
