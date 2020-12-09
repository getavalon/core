import os


def launch(application_path):
    """Setup for Storyboard Pro launch."""
    from avalon import api, storyboardpro, toonboom

    api.install(storyboardpro)

    toonboom.launch(
        application_path,
        os.path.join(os.path.dirname(__file__), "temp.zip")
    )
