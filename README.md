<p align="center">
  <img align="center" src=https://user-images.githubusercontent.com/2152766/27429443-fefb534e-573c-11e7-8b0d-6b99ff1d9870.png>
</p>
<p align="center">
  The safe post-production pipeline
</p>

[![Build Status](https://travis-ci.org/getavalon/core.svg?branch=master)](https://travis-ci.org/getavalon/core) [![Coverage Status](https://coveralls.io/repos/github/getavalon/core/badge.svg?branch=master)](https://coveralls.io/github/getavalon/core?branch=master)

- [Documentation](https://getavalon.github.io)
- [Installation](https://getavalon.github.io/2.0/guides/#install)

<br>

### Testing

```bash
$ cd avalon-core

# One-time build and database
$ docker run --name avalon-mongo -d mongo
$ . build_docker.sh

# Run
$ . test_docker.sh
```

<br>

### Contributing

See [CONTRIBUTING.md](https://github.com/getavalon/core/blob/master/CONTRIBUTING.md) for a summary of guidelines for how you can contribute to Avalon.

Also visit [the chat](https://gitter.im/getavalon/Lobby) for a direct connection with current developers.

<br>

### Code convention

Below are some of the standard practices applied to this repositories.

- **Etiquette: PEP8**
 	- All code is written in PEP8. It is recommended you use a linter as you work, flake8 and pylinter are both good options.
- **Etiquette: Napoleon docstrings**
	- Any docstrings are made in Google Napoleon format. See [Napoleon](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for details.
- **Etiquette: Semantic Versioning**
	- This project follows [semantic versioning](http://semver.org).
- **Etiquette: Underscore means private**
	- Anything prefixed with an underscore means that it is internal to wherever it is used. For example, a variable name is only ever used in the parent function or class. A module is not for use by the end-user. In contrast, anything without an underscore is public, but not necessarily part of the API. Members of the API resides in `api.py`.
- **API: Idempotence**
 	- A public function must be able to be called twice and produce the exact same result. This means no changing of state without restoring previous state when finishing. For example, if a function requires changing the current selection in Autodesk Maya, it must restore the previous selection prior to completing.
