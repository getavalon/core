"""Test Pure Python functionality"""

import sys
import nose
import warnings

from nose_exclude import NoseExclude

warnings.filterwarnings("ignore", category=DeprecationWarning)

if __name__ == "__main__":
    argv = sys.argv[:]
    argv.extend([

        # Sometimes, files from Windows accessed
        # from Linux cause the executable flag to be
        # set, and Nose has an aversion to these
        # per default.
        "--exe",

        "--verbose",
        "--with-doctest",
        "--exclude-dir=avalon/maya",
        "--exclude-dir=avalon/nuke",
        "--exclude-dir=avalon/houdini",
        "--exclude-dir=avalon/photoshop",

        # We can expect any vendors to
        # be well tested beforehand.
        "--exclude-dir=avalon/vendor",
    ])

    nose.main(argv=argv,
              addplugins=[NoseExclude()])
