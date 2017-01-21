"""Pipeline functionality specifically for Nuke

Hi Arvid!

I've pre-filled this module with the functions you'll need to
implement in order to get the Creator, Loader and Manager
running in Nuke.

Have a look at the docstring for each function, and refer back
to the Maya implementation which resides in a similar file but
under the `maya/` directory.

"""


def install():
    """Install Nuke-specific functionality of mindbender-core.

    This is where you install menus and register families, data
    and loaders into Nuke.

    It is called automatically when installing via `api.install(nuke)`.

    See the Maya equivalent for inspiration on how to implement this.

    """


def uninstall():
    """Uninstall all tha was installed

    This is where you undo everything that was done in `install()`.
    That means, removing menus, deregistering families and  data
    and everything. It should be as though `install()` was never run,
    because odds are calling this function means the user is interested
    in re-installing shortly afterwards. If, for example, he has been
    modifying the menu or registered families.

    """


def ls():
    """List available containers.

    This function is used by the Container Manager in Nuke. You'll
    need to implement a for-loop that then *yields* one Container at
    a time.

    See the `container.json` schema for details on how it should look,
    and the Maya equivalent, which is in `mindbender.maya.pipeline`

    """

    yield {}


def load(asset, subset, version=-1, representation=None):
    """Load data into Maya

    This function takes an asset from the Loader GUI and
    imports it into Nuke.

    The function takes `asset`, which is a dictionary following the
    `asset.json` schema, a `subset` of the `subset.json` schema and
    an integer version number and a representation.

    Again, on terminology, see the Terminology chapter in the
    documentation, it'll have info on these for you.

    """

    return ""


def create(name, family, options=None):
    """Create new instance

    This function is called when a user has finished using the
    Creator GUI. It is given a (str) name, a (str) family and
    an optional dictionary of options. You can safely ignore
    the options for a first run and come back to it once
    everything works well.

    """

    return ""


def update(container, version=-1):
    """Update an existing `container` to `version`

    From the Container Manager, once a user chooses to
    update from one version to another, this function is
    called.

    It takes a `container`, which is a dictionary of the
    `container.json` schema, and an integer version.

    """


def remove(container):
    """Remove an existing `container` from Nuke scene

    In the Container Manager, when a user chooses to remove
    a container they've previously imported, this function is
    called.

    You'll need to ensure all nodes that cale along with the
    loaded asset is removed here.

    """
