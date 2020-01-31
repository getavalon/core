"""The safe production pipeline"""

import os
from setuptools import setup, find_packages
from avalon.version import version

# Git is required for deployment
assert len(version.split(".")) == 3, (
    "Could not compute patch version, make sure `git` is\n"
    "available and see version.py for details")

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Utilities",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

# Serialise version from Git revision to patch number
dirname = os.path.dirname(__file__)
fname = os.path.join(dirname, "avalon", "__version__.py")
with open(fname, "w") as f:
    f.write("version = \"%s\"\n" % version)

try:
    setup(
        name="avalon-core",
        version=version,
        description=__doc__,
        long_description=__doc__,
        url="https://github.com/getavalon/core",
        author="Marcus Ottosson",
        author_email="konstruktion@gmail.com",
        license="MIT",
        zip_safe=False,
        packages=find_packages(),
        package_data={
            "avalon": [
                "schema/*.json",
                "style/*.qrc",
                "style/*.qss",
                "style/rc/*.png",
                "fonts/opensans/*.txt",
                "fonts/opensans/*.ttf",
                "vendor/jsonschema/schemas/*.json",
                "vendor/qtawesome/fonts/*.ttf",
                "vendor/qtawesome/fonts/*.json",
            ]
        },
        classifiers=classifiers,
        install_requires=[
            "pymongo>=3.4,<4",
        ],
        python_requires=">2.7, <4",
    )

finally:
    # Clean-up
    os.remove(fname)
