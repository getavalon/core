import os
import sys

import avalon.api
import avalon.fusion

import pyblish_qml


def _install_fusion():

    from pyblish_qml import settings
    import pyblish_qml.host as host

    sys.stdout.write("Setting up Pyblish QML in Fusion\n")

    if settings.ContextLabel == settings.ContextLabelDefault:
        settings.ContextLabel = "Fusion"
    if settings.WindowTitle == settings.WindowTitleDefault:
        settings.WindowTitle = "Pyblish (Fusion)"


print("Starting Pyblish setup..")

# Install avalon
avalon.api.install(avalon.fusion)

# force current working directory to NON FUSION path
os.chdir("C:/")

# install fusion title
_install_fusion()

# Run QML in modal mode so it keeps listening to the
# server in the main thread and keeps this process
# open until QML finishes.
print("Running publish_qml.show(modal=True)..")
pyblish_qml.show(modal=True)
