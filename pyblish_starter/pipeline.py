import os
import datetime

from pyblish import api

_registered_defaults = []
_registered_families = []


def setup():
    register_plugins()

    register_default({
        "key": "id",
        "value": "pyblish.starter.instance"
    })

    register_default({"key": "label", "value": "{name}"})
    register_default({"key": "family", "value": "{family}"})

    register_family({
        "name": "starter.model",
        "help": "Polygonal geometry for animation"
    })

    register_family({
        "name": "starter.rig",
        "help": "Character rig"
    })

    register_family({
        "name": "starter.animation",
        "help": "Pointcache"
    })


def ls(root):
    """List available assets"""
    return os.listdir(os.path.join(root, "public"))


def register_plugins():
    """Register accompanying plugins"""
    from . import plugins
    plugin_path = os.path.dirname(plugins.__file__)
    api.register_plugin_path(plugin_path)


def register_default(item):
    """Register new default attribute

    Dictionary structure:
    {
        "key": "Name of attribute",
        "value": "Value of attribute",
        "help": "Documentation"
    }

    Arguments:
        default (dict): New default Attribute

    """

    assert "key" in item
    assert "value" in item

    _registered_defaults.append(item)


def register_family(item):
    """Register family and attributes for family

    Dictionary structure:
    {
        "name": "Name of attribute",
        "help": "Documentation",
        "attributes": [
            {
                "...": "Same as default",
            }
        ]
    }

    Arguments:
        default (dict): New family

    """

    assert "name" in item

    # If family was already registered then overwrite it
    for i, family in enumerate(_registered_families):
        if item["name"] == family["name"]:
            _registered_families[i] = item
            return

    _registered_families.append(item)


def time():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%SZ")


def format_private_dir(root, name):
    dirname = os.path.join(root, "private", time(), name)
    return dirname
