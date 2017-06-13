import os
import sys
import uuid

import pyblish.api
from maya import cmds, OpenMaya

from . import lib, commands
from .. import api, io
from ..vendor import six
from ..vendor.Qt import QtCore, QtWidgets

self = sys.modules[__name__]
self._menu = "mindbendercore"
self._events = dict()
self._parent = {
    widget.objectName(): widget
    for widget in QtWidgets.QApplication.topLevelWidgets()
}.get("MayaWindow")


def install():
    """Install Maya-specific functionality of mindbender-core.

    This function is called automatically on calling `api.install(maya)`.

    """

    try:
        import pyblish_maya
        assert pyblish_maya.is_setup()

    except (ImportError, AssertionError):
        raise ImportError("mindbender-core depends on pyblish-maya.")

    _install_menu()

    _register_formats()
    _register_plugins()
    _register_loaders()
    _register_creators()

    _register_callbacks()


def uninstall():
    _uninstall_menu()

    api.deregister_format(".ma")
    api.deregister_format(".mb")
    api.deregister_format(".abc")


def _install_menu():
    from ..tools import (
        creator,
        loader,
        manager
    )

    from . import interactive

    _uninstall_menu()

    def deferred():
        cmds.menu(self._menu,
                  label="Mindbender",
                  tearOff=True,
                  parent="MayaWindow")

        cmds.menuItem("Show Creator",
                      command=lambda *args: creator.show(parent=self._parent))
        cmds.menuItem("Show Loader",
                      command=lambda *args: loader.show(parent=self._parent))
        cmds.menuItem("Show Manager",
                      command=lambda *args: manager.show(parent=self._parent))

        cmds.menuItem(divider=True)

        # Modeling sub-menu
        cmds.menuItem("Modeling",
                      label="Modeling",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Combine", command=interactive.combine)

        # Rigging sub-menu
        cmds.menuItem("Rigging",
                      label="Rigging",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Auto Connect", command=interactive.auto_connect)
        cmds.menuItem("Clone (Local)", command=interactive.clone_localspace)
        cmds.menuItem("Clone (World)", command=interactive.clone_worldspace)
        cmds.menuItem("Clone (Special)", command=interactive.clone_special)
        cmds.menuItem("Create Follicle", command=interactive.follicle)

        # Animation sub-menu
        cmds.menuItem("Animation",
                      label="Animation",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Set Defaults", command=interactive.set_defaults)

        cmds.menuItem("System",
                      label="System",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Reload Pipeline", command=_reload)

        cmds.setParent("..", menu=True)

        cmds.menuItem(divider=True)

        cmds.menuItem("Auto Connect", command=interactive.auto_connect_assets)
        cmds.menuItem("Reset Frame Range",
                      command=interactive.reset_frame_range)

    # Allow time for uninstallation to finish.
    QtCore.QTimer.singleShot(100, deferred)


def _reload(*args):
    """Attempt to reload pipeline at run-time.

    CAUTION: This is primarily for development and debugging purposes.

    """

    from mindbender import api, pipeline, io, lib
    import mindbender.maya
    import mindbender.maya.pipeline
    import mindbender.maya.interactive
    import mindbender.maya.commands
    import mindbender.tools.creator.app
    import mindbender.tools.manager.app
    import mindbender.tools.loader.app

    api.uninstall()

    for module in (io,
                   lib,
                   pipeline,
                   mindbender.maya.commands,
                   mindbender.maya.interactive,
                   mindbender.maya.pipeline,
                   mindbender.maya.lib,
                   mindbender.tools.loader.app,
                   mindbender.tools.creator.app,
                   mindbender.tools.manager.app,
                   api,
                   mindbender.maya):
        reload(module)

    api.install(mindbender.maya)


def _uninstall_menu():
    app = QtWidgets.QApplication.instance()
    widgets = dict((w.objectName(), w) for w in app.allWidgets())
    menu = widgets.get(self._menu)

    if menu:
        menu.deleteLater()
        del(menu)


def _register_formats():
    # These file-types will appear in the Loader GUI
    api.register_format(".ma")
    api.register_format(".mb")
    api.register_format(".abc")


def _register_plugins():
    lib_py_path = sys.modules[__name__].__file__
    package_path = os.path.dirname(lib_py_path)
    plugin_path = os.path.join(package_path, "plugins")
    pyblish.api.register_plugin_path(plugin_path)


def _register_loaders():
    lib_py_path = sys.modules[__name__].__file__
    package_path = os.path.dirname(lib_py_path)
    plugin_path = os.path.join(package_path, "loaders")
    api.register_plugin_path(api.Loader, plugin_path)


def _register_creators():
    lib_py_path = sys.modules[__name__].__file__
    package_path = os.path.dirname(lib_py_path)
    plugin_path = os.path.join(package_path, "creators")
    api.register_plugin_path(api.Creator, plugin_path)


def containerise(name,
                 namespace,
                 nodes,
                 context,
                 loader=None,
                 suffix="_CON"):
    """Bundle `nodes` into an assembly and imprint it with metadata

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        nodes (list): Long names of nodes to containerise
        namespace (str): Namespace under which to host container
        asset (mindbender-core:asset-1.0): Current asset
        subset (mindbender-core:subset-1.0): Current subset
        version (mindbender-core:version-1.0): Current version
        representation (mindbender-core:representation-1.0): ...
        loader (str, optional): Name of loader used to produce this container.
        suffix (str, optional): Suffix of container, defaults to `_CON`.

    Returns:
        container (str): Name of container assembly

    """

    container = cmds.sets(nodes, name="%s_%s_%s" % (namespace, name, suffix))

    data = [
        ("id", "pyblish.mindbender.container"),
        ("name", name),
        ("namespace", namespace),
        ("loader", str(loader)),
        ("project", context["project"]["name"]),
        ("asset", context["asset"]["name"]),
        ("subset", context["subset"]["name"]),
        ("version", context["version"]["name"]),
        ("representation", context["representation"]["_id"]),
    ]

    for key, value in data:
        if not value:
            continue

        if isinstance(value, (int, float)):
            cmds.addAttr(container, longName=key, attributeType="short")
            cmds.setAttr(container + "." + key, value)

        else:
            cmds.addAttr(container, longName=key, dataType="string")
            cmds.setAttr(container + "." + key, value, type="string")

    # Hide in outliner
    cmds.setAttr(container + ".verticesOnlySet", True)

    return container


def ls():
    """List containers from active Maya scene

    This is the host-equivalent of api.ls(), but instead of listing
    assets on disk, it lists assets already loaded in Maya; once loaded
    they are called 'containers'

    """

    for container in sorted(lib.lsattr("id", "pyblish.mindbender.container")):
        data = lib.read(container)

        try:
            document = io.find_one(
                {"_id": io.ObjectId(data["representation"])}
            )
        except io.InvalidId:
            api.logger.warning("Skipping %s, invalid id." % container)
            continue

        data = dict(
            schema="mindbender-core:container-1.0",
            objectName=container,
            name=data["name"],
            namespace=data["namespace"],
            representation=data["representation"],
            **document["data"]
        )

        yield data


def load(representation,
         name=None,
         namespace=None,
         post_process=True,
         preset=None):
    """Load asset via database

    Arguments:
        representation (dict, io.ObjectId or str): Address to representation

    """

    assert representation is not None, "This is a bug"

    preset = preset or os.environ["MINDBENDER_TASK"]

    if isinstance(representation, (six.string_types, io.ObjectId)):
        representation = io.find_one({"_id": io.ObjectId(str(representation))})

    version, subset, asset, project = io.parenthood(representation)

    assert all([representation, version, subset, asset, project]), (
        "This is a bug"
    )

    context = {
        "project": project,
        "asset": asset,
        "subset": subset,
        "version": version,
        "representation": representation,
        "preset": {"name": preset}
    }

    name = name or subset["name"]
    namespace = namespace or lib.unique_namespace(
        asset["name"] + "_",
        prefix="_" if asset["name"][0].isdigit() else "",
        suffix="_",
    )

    nodes = list()
    loaders = list()
    families = context["version"]["data"]["families"]
    for Loader in api.discover(api.Loader):
        has_family = any(family in Loader.families for family in families)
        has_representation = representation["name"] in Loader.representations

        if has_family and has_representation:
            Loader.log.info(
                "Running '%s' on '%s'" % (Loader.__name__, asset["name"])
            )

            try:
                loader = Loader(context)
                loader.process(name, namespace, context)
            except OSError as e:
                print("WARNING: %s" % e)
                continue

            if post_process:
                loader.post_process(name, namespace, context)

            loaders.append(Loader)
            nodes.extend(loader)

    assert loaders, "No loaders were run, this is a bug"
    assert nodes, "No nodes were loaded, this is a bug"

    return containerise(
        name=name,
        namespace=namespace,
        nodes=nodes,
        context=context,
        loader=" ".join(Loader.__name__ for Loader in loaders)
    )


class Creator(api.Creator):
    def process(self):
        nodes = list()

        if (self.options or {}).get("useSelection"):
            nodes = cmds.ls(selection=True)

        instance = cmds.sets(nodes, name=self.name)
        lib.imprint(instance, self.data)


def create(name, asset, family, options=None, data=None):
    """Create a new instance

    Associate nodes with a subset and family. These nodes are later
    validated, according to their `family`, and integrated into the
    shared environment, relative their `subset`.

    Data relative each family, along with default data, are imprinted
    into the resulting objectSet. This data is later used by extractors
    and finally asset browsers to help identify the origin of the asset.

    Arguments:
        name (str): Name of subset
        asset (str): Name of asset
        family (str): Name of family
        options (dict, optional): Additional options from GUI
        data (dict, optional): Additional data from GUI

    Raises:
        NameError on `subset` already exists
        KeyError on invalid dynamic property
        RuntimeError on host error

    Returns:
        Instance as str

    """

    # Default data
    _data = {
        "id": "pyblish.mindbender.instance",
        "family": family,
        "asset": asset,
        "subset": name
    }

    if data is not None:
        data.update(_data)
    else:
        data = _data

    for Plugin in api.discover(api.Creator):
        has_family = family == Plugin.family

        if not has_family:
            continue

        Plugin.log.info(
            "Creating '%s' with '%s'" % (name, Plugin.__name__)
        )

        plugin = Plugin(name, asset, options, data)

        with lib.maintained_selection():
            plugin.process()


def _create(name, family, asset=None, options=None, data=None):

    family_ = api.registered_families().get(family)

    assert family_ is not None, "{0} is not a valid family".format(
        family)

    # Merge incoming with existing data
    # TODO(marcus): This is being delegated to Creator plug-ins.
    data = dict(
        dict(api.registered_data(), **family_.get("data", {})),
        **(data or {})
    )

    instance = "%s_SET" % name
    asset = asset or os.environ["MINDBENDER_ASSET"]

    if cmds.objExists(instance):
        raise NameError("\"%s\" already exists." % instance)

    with lib.maintained_selection():
        nodes = list()

        if (options or {}).get("useSelection"):
            nodes = cmds.ls(selection=True)

        instance = cmds.sets(nodes, name=instance)

    # Resolve template
    for key, value in data.items():
        if isinstance(value, basestring):
            try:
                data[key] = str(value).format(
                    subset=name,
                    asset=asset,
                    family=family_["name"]
                )
            except KeyError as e:
                raise KeyError("Invalid dynamic property: %s" % e)

    lib.imprint(instance, data)

    return instance


def update(container, version=-1):
    """Update `container` to `version`

    This function relies on a container being referenced. At the time of this
    writing, all assets - models, rigs, animations, shaders - are referenced
    and should pose no problem. But should there be an asset that isn't
    referenced then this function will need to see an update.

    Arguments:
        container (mindbender-core:container-1.0): Container to update,
            from `host.ls()`.
        version (int, optional): Update the container to this version.
            If no version is passed, the latest is assumed.

    """

    node = container["objectName"]

    # Assume asset has been referenced
    reference_node = next((node for node in cmds.sets(node, query=True)
                          if cmds.nodeType(node) == "reference"), None)

    assert reference_node, ("Imported container not supported; "
                            "container must be referenced.")

    current_representation = io.find_one({
        "_id": io.ObjectId(container["representation"])
    })

    assert current_representation is not None, "This is a bug"

    version_, subset, asset, project = io.parenthood(current_representation)

    if version == -1:
        new_version = io.find_one({
            "type": "version",
            "parent": subset["_id"]
        }, sort=[("name", -1)])
    else:
        new_version = io.find_one({
            "type": "version",
            "parent": subset["_id"],
            "name": version,
        })

    new_representation = io.find_one({
        "type": "representation",
        "parent": new_version["_id"],
        "name": current_representation["name"]
    })

    assert new_version is not None, "This is a bug"

    template_publish = project["config"]["template"]["publish"]
    fname = template_publish.format(**{
        "root": api.registered_root(),
        "project": project["name"],
        "asset": asset["name"],
        "silo": asset["silo"],
        "subset": subset["name"],
        "version": new_version["name"],
        "representation": current_representation["name"],
    })

    file_type = {
        "ma": "mayaAscii",
        "mb": "mayaBinary",
        "abc": "Alembic"
    }.get(new_representation["name"])

    assert file_type, ("Unsupported representation: %s" % new_representation)

    assert os.path.exists(fname), "%s does not exist." % fname
    cmds.file(fname, loadReference=reference_node, type=file_type)

    # Update metadata
    cmds.setAttr(container["objectName"] + ".version",
                 new_version["name"])
    cmds.setAttr(container["objectName"] + ".representation",
                 str(new_representation["_id"]),
                 type="string")


def remove(container):
    """Remove an existing `container` from Maya scene

    Arguments:
        container (mindbender-core:container-1.0): Which container
            to remove from scene.

    """

    node = container["objectName"]

    # Assume asset has been referenced
    reference_node = next((node for node in cmds.sets(node, query=True)
                          if cmds.nodeType(node) == "reference"), None)

    assert reference_node, ("Imported container not supported; "
                            "container must be referenced.")

    print("Removing '%s' from Maya.." % container["name"])

    namespace = cmds.referenceQuery(reference_node, namespace=True)
    fname = cmds.referenceQuery(reference_node, filename=True)
    cmds.file(fname, removeReference=True)

    try:
        # If container is not automatically cleaned up by May (issue #118)
        cmds.namespace(removeNamespace=namespace, deleteNamespaceContent=True)
    except RuntimeError:
        pass


def _register_callbacks():
    for handler, event in self._events.copy().items():
        if event is None:
            continue

        try:
            OpenMaya.MMessage.removeCallback(event)
            self._events[handler] = None
        except RuntimeError, e:
            print(e)

    self._events[_on_scene_save] = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kBeforeSave, _on_scene_save
    )

    self._events[_on_scene_new] = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kAfterNew, _on_scene_new
    )

    print("Installed event handler __on_scene_save..")
    print("Installed event handler _on_scene_new..")


def _set_uuid(node):
    """Add mbID to `node`

    Unless one already exists.

    """

    attr = "{0}.mbID".format(node)

    if not cmds.objExists(attr):
        cmds.addAttr(node, longName="mbID", dataType="string")
        _, uid = str(uuid.uuid4()).rsplit("-", 1)
        cmds.setAttr(attr, uid, type="string")


def _on_scene_new(_):
    print("Running scene new..")
    commands.reset_frame_range()


def _on_scene_save(_):
    """Automatically add IDs to new nodes

    Any transform of a mesh, without an exising ID,
    is given one automatically on file save.

    """

    nodes = (set(cmds.ls(type="mesh", long=True)) -
             set(cmds.ls(long=True, readOnly=True)) -
             set(cmds.ls(long=True, lockedNodes=True)))

    transforms = cmds.listRelatives(list(nodes), parent=True) or list()

    # Add unique identifiers
    for node in transforms:
        _set_uuid(node)
