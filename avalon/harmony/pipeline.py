import pyblish.api


def install():
    """Install Photoshop-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(photoshop)`.
    """
    print("Installing Avalon Harmony...")
    pyblish.api.register_host("harmony")


def ls():
    pass
