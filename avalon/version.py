"""Version includes the Git revision number

This module separates between deployed and development versions of allzpark.
A development version draws its minor version directly from Git, the total
number of commits on the current branch equals the revision number. Once
deployed, this number is embedded into the Python package.

"""

VERSION_MAJOR = 5
VERSION_MINOR = 5
VERSION_PATCH = 0

version = "%s.%s" % (VERSION_MAJOR, VERSION_MINOR)

try:
    # Look for serialised version
    from .__version__ import version

except ImportError:
    # Else, we're likely running out of a Git repository
    import os as _os
    import subprocess as _subprocess

    try:
        # If used as a git repository
        _cwd = _os.path.dirname(__file__)
        VERSION_PATCH = int(_subprocess.check_output(
            ["git", "rev-list", "HEAD", "--count"],

            cwd=_cwd,

            # Ensure strings are returned from both Python 2 and 3
            universal_newlines=True,

        ).rstrip())

        # Builds since previous minor version
        VERSION_PATCH -= 1489
        VERSION_PATCH -= 83
        VERSION_PATCH -= 86

    except Exception:
        # Otherwise, no big deal
        pass

    else:
        version += ".%s" % VERSION_PATCH

version_info = list(map(int, version.split(".")))
__version__ = version

__all__ = ["version", "version_info", "__version__"]
