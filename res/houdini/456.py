123

import hou

HOU_ACCESS = 2

# Set Environment
# -----------------------------------------------------------------------------
hou.hscript('set -g HOUDINI_ACCESS_METHOD = {0}'.format(HOU_ACCESS ))
print('Environment variables set.')
