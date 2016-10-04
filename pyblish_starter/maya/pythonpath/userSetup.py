from maya import cmds
from pyblish_starter import install, maya

# Allow time for dependencies (e.g. pyblish-maya)
# to be installed first.
cmds.evalDeferred(lambda: install(maya))
