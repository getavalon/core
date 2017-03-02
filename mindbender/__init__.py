"""This module holds state.

Modules in this package may modify state.

Erasing the contents `_state` will completely zero out
the currently held state of mindbender-core.

"""

_state = {

    # Data associated to a family, such as `startFrame`
    # for `mindbender.animation`.
    "data": dict(),

    # Known families, such as `mindbender.rig` and `mindbender.model`
    "families": dict(),

    # Known formats, such as `.ma` and `.abc`.
    "formats": list(),

    # Known silos, such as `assets` and `film`.
    "silos": set(),

    # Known absolute paths to loaders
    "loader_paths": set(),

    # Current root
    "root": "",

    # Current host
    "host": None,
}
