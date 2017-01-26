"""Model Identifier

Establish a relationship between a model and shader that doesn't
rely on name. Instead, a shader is related to a short identifier
that remains with an object even when duplicated.

"""

import sys
import uuid

from maya import cmds, OpenMaya

from .. import api

self = sys.modules[__name__]
self._mid_callback = None


def register_callback():
    """Automatically add IDs to new nodes

    Any transform of a mesh, without an exising ID,
    is given one automatically on file save.

    """

    if self._mid_callback is not None:
        try:
            OpenMaya.MMessage.removeCallback(self._mid_callback)
            self._mid_callback = None
        except RuntimeError, e:
            api.echo(e)

    self._mid_callback = OpenMaya.MSceneMessage.addCallback(
        OpenMaya.MSceneMessage.kBeforeSave, _callback
    )

    api.echo("Registered _callback")


def _set_uuid(node):
    """Add mbID to `node`

    Unless one already exists.

    """

    attr = "{0}.mbID".format(node)

    if not cmds.objExists(attr):
        cmds.addAttr(node, longName="mbID", dataType="string")
        _, uid = str(uuid.uuid4()).rsplit("-", 1)
        cmds.setAttr(attr, uid, type="string")


def _callback(_):
    nodes = (set(cmds.ls(type="mesh", long=True)) -
             set(cmds.ls(long=True, readOnly=True)) -
             set(cmds.ls(long=True, lockedNodes=True)))

    transforms = cmds.listRelatives(list(nodes), parent=True)

    # Add unique identifiers
    for node in transforms:
        _set_uuid(node)
