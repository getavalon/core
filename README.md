### Pyblish Mindbender

[![Build Status](https://travis-ci.org/pyblish/pyblish-mindbender.svg?branch=master)](https://travis-ci.org/pyblish/pyblish-mindbender) [![Coverage Status](https://coveralls.io/repos/github/pyblish/pyblish-mindbender/badge.svg?branch=master)](https://coveralls.io/github/pyblish/pyblish-mindbender?branch=master) [![PyPI version](https://badge.fury.io/py/pyblish-mindbender.svg)](https://pypi.python.org/pypi/pyblish-mindbender)

A basic asset creation pipeline - batteries included.

- [Website](http://pyblish.com/pyblish-mindbender)
- [Forums](http://forums.pyblish.com)

<br>

### Install

```bash
$ pip install pyblish-mindbender
```

Each studio must then define a few executables with their own local paths, that are later mapped into the pipeline automatically.

<br>

### Usage

```python
>>> from pyblish_mindbender import api, maya
>>> api.install(maya)
```

<br>

### Testing

```bash
cd pyblish-mindbender
docker build -t pyblish/mindbender -f Dockerfile-maya2016 .

# Run nosetests (Windows)
docker run --rm -v %cd%:/workspace pyblish/mindbender

# Run nosetests (Linux/OSX)
docker run --rm -v $(pwd):/workspace pyblish/mindbender
```

<br>

### Code convention

Below are some of the standard practices applied to this repositories.

- **PEP8**
 	- All code is written in PEP8. It is recommended you use a linter as you work, flake8 and pylinter are both good options.
- **Napoleon docstrings**
	- Any docstrings are made in Google Napoleon format. See [Napoleon](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for details.
- **Semantic Versioning**
	- This project follows [semantic versioning](http://semver.org).
- **Underscore means private**
	- Anything prefixed with an underscore means that it is internal to wherever it is used. For example, a variable name is only ever used in the parent function or class. A module is not for use by the end-user. In contrast, anything without an underscore is public, but not necessarily part of the API. Members of the API resides in `api.py`.
