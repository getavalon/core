"""PyPI setup script

Usage:
    >>> python setup.py sdist
    ...

"""

import os
import imp
from setuptools import setup, find_packages

version_file = os.path.abspath("pyblish_starter/version.py")
version_mod = imp.load_source("version", version_file)
version = version_mod.version

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.1",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities"
]

setup(
    name="pyblish-starter",
    version=version,
    description="Build your own publishing pipeline, "
                "starting with the basics.",
    author="Pyblish",
    author_email="marcus@abstractfactory.com",
    url="https://github.com/pyblish/pyblish-starter",
    license="LGPL",
    packages=find_packages(),
    classifiers=classifiers,
    install_requires=[
        "pyblish-base>=1.4.2",
        "pyblish-maya>=2.1"
    ],
    package_data={
        "pyblish_starter": [
            "maya/pythonpath/*.py",
            "schema/*.json",
            "vendor/jsonschema/schemas/*.json"
        ]
    },
    entry_points={},
)
