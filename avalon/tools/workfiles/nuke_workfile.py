import sys
import subprocess


def main(path):
    import nuke
    nuke.scriptSaveAs(filename=path)


if __name__ == "__main__":
    # Called initially
    if len(sys.argv) == 3:
        executable_path = sys.argv[1].replace("\\", "/").lower()
        file_path = sys.argv[2].replace("\\", "/").lower()

        # Launching Nuke in terminal mode with interactive license.
        subprocess.call([executable_path, "-i", "-t", __file__, file_path])

    # Called from above subprocess
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        main(file_path)
