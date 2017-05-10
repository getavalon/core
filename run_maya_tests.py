"""Use Mayapy for testing

Usage:
    $ mayapy run_maya_tests.py

"""

import sys
import nose
import logging
import warnings

from nose_exclude import NoseExclude

warnings.filterwarnings("ignore", category=DeprecationWarning)

if __name__ == "__main__":
    from maya import standalone
    standalone.initialize()

    log = logging.getLogger()

    # Discard default Maya logging handler
    log.handlers[:] = []

    argv = sys.argv[:]
    argv.extend([

        # Sometimes, files from Windows accessed
        # from Linux cause the executable flag to be
        # set, and Nose has an aversion to these
        # per default.
        "--exe",

        "--verbose",
        "--with-doctest",

        "--with-coverage",
        "--cover-html",
        "--cover-tests",
        "--cover-erase",

        "--exclude-dir=mindbender/nuke",
        "--exclude-dir=mindbender/houdini",
        "--exclude-dir=mindbender/schema",
        "--exclude-dir=mindbender/plugins",

        # We can expect any vendors to
        # be well tested beforehand.
        "--exclude-dir=mindbender/vendor",
    ])

    nose.main(argv=argv,
              addplugins=[NoseExclude()])
