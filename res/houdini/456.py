123
# Imports
import hou

HOU_ACCESS = 2 # --- HOUDINI_ACCESS_METHOD

# Set Environment
# -----------------------------------------------------------------------------

try:
    hou.hscript('set -g HOUDINI_ACCESS_METHOD = {0}'.format(HOU_ACCESS )) # HOUDINI_ACCESS_METHOD

    print('Environment variables set.')

except:
    print("Could not set environment variables.")


# Success messages
print("456.cmd successfully executed.")
