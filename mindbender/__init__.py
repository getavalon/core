"""This module holds state.

Modules in this package may modify state.

Erasing the contents of each container below will completely zero out
the currently held state of mindbender-core.

"""

_registered_data = dict()
_registered_families = dict()
_registered_formats = list()
_registered_loaders = list()
_registered_silos = set()
_registered_loader_paths = set()
_registered_root = {"_": ""}
_registered_host = {"_": None}
