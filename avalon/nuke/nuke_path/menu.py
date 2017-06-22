import logging

import nuke

logging.basicConfig(level=logging.INFO)


def add_to_filemenu():
    menubar = nuke.menu("Nuke")
    menu = menubar.menu("File")

    menu.addSeparator(index=8)

    cmd_qml = "import pyblish_qml;pyblish_qml.show()"
    cmd_lite = "import pyblish_lite;pyblish_lite.show()"
    menu.addCommand("Publish (QML)", cmd_qml, index=9)
    menu.addCommand("Publish (Lite)", cmd_lite, index=10)

    menu.addSeparator(index=11)


try:
    __import__("pyblish_nuke")
    __import__("pyblish")

except ImportError as e:
    nuke.tprint("pyblish: Could not load integration: %s " % e)

else:

    import pyblish_nuke

    # Setup integration
    pyblish_nuke.setup(menu=False)
    add_to_filemenu()
