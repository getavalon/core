import os
import datetime

from pyblish import api

_defaults = []
_families = []


def setup():
    register_plugins()


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

    _defaults.append(item)


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
    for i, family in enumerate(_families):
        if item["name"] == family["name"]:
            _families[i] = item
            return

    _families.append(item)


def time():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%SZ")


def format_private_dir(root, name):
    dirname = os.path.join(root, "private", time(), name)
    return dirname
