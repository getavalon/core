import hou

HOU_ACCESS = 2

# Set Environment
# -----------------------------------------------------------------------------

try:
    hou.hscript('set -g HOUDINI_ACCESS_METHOD = {0}'.format(HOU_ACCESS ))
    print('Environment variables set.')

# Success messages
print("456.cmd successfully executed.")
