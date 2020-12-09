import pyblish.api


def install():
    """Install Storyboard Pro specific functionality of avalon-core.

    This function is called automatically on calling
    `api.install(storyboardpro)`.
    """
    print("Installing Avalon Storyboard Pro...")
    pyblish.api.register_host("storyboardpro")


def ls():
    """Yields containers from Harmony scene.

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Harmony; once loaded
    they are called 'containers'.

    Yields:
        dict: container
    """
    pass
