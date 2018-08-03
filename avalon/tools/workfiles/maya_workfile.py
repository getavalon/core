import sys
import subprocess


def main(path):
    import maya.standalone

    maya.standalone.initialize(name='python')

    from maya import cmds

    cmds.file(rename=path)

    file_type = "mayaBinary"
    if path.endswith(".ma"):
        file_type = "mayaAscii"

    cmds.file(save=True, type=file_type)


if __name__ == "__main__":
    # Called initially
    if len(sys.argv) == 3:
        executable_path = sys.argv[1].replace("\\", "/").lower()
        file_path = sys.argv[2].replace("\\", "/").lower()
        subprocess.call([executable_path, __file__, file_path])

    # Called from above subprocess
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        main(file_path)
