"""Compatibility

This module is to ensure the compatibility between Maya, Avalon and Pyblish
is maintained.
"""
import maya.cmds as cmds
import os
import logging

import avalon.pipeline

log = logging.getLogger(__name__)

create = avalon.pipeline.create


def remove_googleapiclient():
    """Check if the compatibility must be maintained

    The Maya 2018 version tries to import the `http` module from
    Maya2018/plug-ins/MASH/scripts/googleapiclient/http.py in stead of the
    module from six.py. This import conflict causes a crash Avalon's publisher.
    This is due to Autodesk adding paths to the PYTHONPATH environment variable
    which contain modules instead of only packages.
    """

    keyword = "googleapiclient"

    # reconstruct python paths
    python_paths = os.environ["PYTHONPATH"].split(os.pathsep)
    paths = [path for path in python_paths if keyword not in path]
    os.environ["PYTHONPATH"] = os.pathsep.join(paths)


def install():
    """Run all compatibility functions"""
    if cmds.about(version=True) == "2018":
        remove_googleapiclient()


def load(Loader,
         representation,
         name=None,
         namespace=None,
         data=None):
    """Load asset via database

    Deprecated; this functionality is replaced by `api.load()`

    Arguments:
        Loader (api.Loader): The loader to process in host Maya.
        representation (dict, io.ObjectId or str): Address to representation
        name (str, optional): Use pre-defined name
        namespace (str, optional): Use pre-defined namespace
        data (dict, optional): Additional settings dictionary

    """

    from avalon.vendor import six
    from avalon import io
    from avalon.maya import lib
    from avalon.maya.pipeline import containerise

    assert representation is not None, "This is a bug"

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
    }

    # Ensure data is a dictionary when no explicit data provided
    if data is None:
        data = dict()
    assert isinstance(data, dict), "Data must be a dictionary"

    name = name or subset["name"]
    namespace = namespace or lib.unique_namespace(
        asset["name"] + "_",
        prefix="_" if asset["name"][0].isdigit() else "",
        suffix="_",
    )

    # TODO(roy): add compatibility check, see `tools.loader.lib`

    Loader.log.info(
        "Running '%s' on '%s'" % (Loader.__name__, asset["name"])
    )

    try:
        loader = Loader(context)

        with lib.maintained_selection():
            loader.process(name, namespace, context, data)

    except OSError as e:
        log.info("WARNING: %s" % e)
        return list()

    # Only containerize if any nodes were loaded by the Loader
    nodes = loader[:]
    if not nodes:
        return

    return containerise(
        name=name,
        namespace=namespace,
        nodes=loader[:],
        context=context,
        loader=Loader.__name__)


def update(container, version=-1):
    """Update `container` to `version`

    Deprecated; this functionality is replaced by `api.update()`

    This function relies on a container being referenced. At the time of this
    writing, all assets - models, rigs, animations, shaders - are referenced
    and should pose no problem. But should there be an asset that isn't
    referenced then this function will need to see an update.

    Arguments:
        container (avalon-core:container-1.0): Container to update,
            from `host.ls()`.
        version (int, optional): Update the container to this version.
            If no version is passed, the latest is assumed.

    """

    from avalon import io
    from avalon import api

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
    cmds.setAttr(container["objectName"] + ".representation",
                 str(new_representation["_id"]),
                 type="string")


def remove(container):
    """Remove an existing `container` from Maya scene

    Deprecated; this functionality is replaced by `api.remove()`

    Arguments:
        container (avalon-core:container-1.0): Which container
            to remove from scene.

    """

    node = container["objectName"]

    # Assume asset has been referenced
    reference_node = next((node for node in cmds.sets(node, query=True)
                          if cmds.nodeType(node) == "reference"), None)

    assert reference_node, ("Imported container not supported; "
                            "container must be referenced.")

    log.info("Removing '%s' from Maya.." % container["name"])

    namespace = cmds.referenceQuery(reference_node, namespace=True)
    fname = cmds.referenceQuery(reference_node, filename=True)
    cmds.file(fname, removeReference=True)

    try:
        cmds.delete(node)
    except ValueError:
        # Already implicitly deleted by Maya upon removing reference
        pass

    try:
        # If container is not automatically cleaned up by May (issue #118)
        cmds.namespace(removeNamespace=namespace, deleteNamespaceContent=True)
    except RuntimeError:
        pass


class BackwardsCompatibleLoader(avalon.pipeline.Loader):
    """A backwards compatible loader.

    This triggers the old-style `process` through the old Maya's host `load`,
    `update` and `remove` methods and exposes it through the new-style Loader
    api.

    Note: This inherits from `avalon.pipeline.Loader` and *not* from
        `avalon.maya.pipeline.Loader`

    """

    def load(self,
             context,
             name=None,
             namespace=None,
             data=None):
        return load(Loader=self.__class__,
                    representation=context['representation'],
                    name=name,
                    namespace=namespace,
                    data=data)

    def remove(self, container):
        return remove(container)

    def update(self, container, representation):
        version = representation['context']['version']
        return update(container, version=version)
