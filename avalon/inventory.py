"""Utilities for interacting with database through the Inventory API

Until assets are created entirely in the database, this script
provides a bridge between the file-based project inventory and configuration.

Usage:
    $ # Create new project:
    $ python -m avalon.inventory --init
    $ python -m avalon.inventory --save

    $ # Manage existing project
    $ python -m avalon.inventory --load
    $ # Update the .inventory.toml or .config.toml
    $ python -m avalon.inventory --save

"""

import os
import sys
import copy

from avalon import schema, io
from avalon.vendor import toml

self = sys.modules[__name__]
self.collection = None

__all__ = [
    "init",
    "save",
    "load",
]


DEFAULTS = {
    "config": {
        "schema": "avalon-core:config-1.0",
        "apps": [
            {
                "name": "shell",
                "label": "Shell"
            },
            {
                "name": "maya2016",
                "label": "Autodesk Maya 2016"
            },
            {
                "name": "nuke10",
                "label": "The Foundry Nuke 10.0"
            },
        ],
        "tasks": [
            {"name": "model"},
            {"name": "render"},
            {"name": "animate"},
            {"name": "rig"},
            {"name": "lookdev"},
            {"name": "layout"},
        ],
        "template": {
            "work":
                "{root}/{project}/{silo}/{asset}/work/"
                "{task}/{app}",
            "publish":
                "{root}/{project}/{silo}/{asset}/publish/"
                "{subset}/v{version:0>3}/{subset}.{representation}"
        }
    },
    "inventory": {
        "schema": "avalon-core:inventory-1.0",
        "assets": [
            {
                "name": "hero",
                "label": "Hero"
            },
            {
                "name": "villain"
            }
        ],
        "film": [
            {
                "name": "shot1",
                "frameStart": 1000,
                "frameEnd": 1143
            },
            {
                "name": "shot2",
                "frameStart": 1000,
                "frameEnd": 1081
            },
        ]
    }
}


def create_project(name):
    if io.find_one({"type": "project", "name": name}):
        raise RuntimeError("%s already exists" % name)

    return io.insert_one({
        "schema": "avalon-core:project-2.0",
        "type": "project",
        "name": name,
        "data": dict(),
        "config": DEFAULTS["config"],
        "parent": None,
    }).inserted_id


def create_asset(name, silo, data, parent):
    assert isinstance(parent, io.ObjectId)
    if io.find_one({"type": "asset", "name": name}):
        raise RuntimeError("%s already exists" % name)

    return io.insert_one({
        "schema": "avalon-core:asset-2.0",
        "name": name,
        "silo": silo,
        "parent": parent,
        "type": "asset",
        "data": data
    }).inserted_id


def save(name, config, inventory):
    """Write `config` and `inventory` to database as `name`

    Given a configuration and inventory, this function writes
    the changes to the current database.

    Arguments:
        name (str): Project name
        config (dict): Current configuration
        inventory (dict): Current inventory

    """

    config = copy.deepcopy(config)
    inventory = copy.deepcopy(inventory)

    if "config" not in config.get("schema", ""):
        raise schema.SchemaError("Missing schema for config")

    if "inventory" not in inventory.get("schema", ""):
        raise schema.SchemaError("Missing schema for inventory")

    handlers = {
        "avalon-core:inventory-1.0": _save_inventory_1_0,
        "avalon-core:config-1.0": _save_config_1_0
    }

    for data in (inventory, config):
        try:
            schema_ = data.get("schema")
            handler = handlers[schema_]

        except KeyError:
            raise schema.SchemaError(
                "ERROR: Missing handler for %s)" % (schema))

        else:
            schema.validate(data)
            print("Saving %s.." % schema_)
            handler(name, data)


def init(name):
    """Initialise a new project called `name`

    Upon creating a new project, call init to establish an example
    inventory and configuration for your project.

    Arguments:
        name (str): Name of new project

    """

    project = io.find_one({"type": "project"})

    if project is not None:
        raise Exception("'%s' already exists, "
                        "try --load instead" % project["name"])

    config = DEFAULTS["config"]
    inventory = DEFAULTS["inventory"]

    return config, inventory


def load(name):
    """Read project called `name` from database

    Arguments:
        name (str): Project name

    """

    print("Loading .inventory.toml and .config.toml..")

    project = io.find_one({"type": "project"})

    if project is None:
        msg = "'{0}' not found, try --init to start a new project".format(name)

        projects = ""
        for project in io.projects():
            projects += "\n- {0}".format(project["name"])

        if projects:
            msg += (
                ", or load a project from the database.\nProjects:{1}".format(
                    name, projects
                )
            )
        else:
            msg += "."

        raise Exception(msg)

    else:
        config = project["config"]
        inventory = {"schema": "avalon-core:inventory-1.0"}
        for asset in io.find({"type": "asset", "parent": project["_id"]}):
            silo = asset["silo"]
            data = asset["data"]

            data.pop("visualParent", None)  # Hide from manual editing

            if silo not in inventory:
                inventory[silo] = list()

            inventory[silo].append(dict(data, **{"name": asset["name"]}))

            for key, value in project["data"].items():
                inventory[key] = value

    config = dict(
        DEFAULTS["config"],
        **config
    )

    return config, inventory


def ls():
    """Return a list of project names in database."""

    return [project["name"] for project in io.projects()]


def _save_inventory_1_0(project_name, data):
    data.pop("schema")

    # Separate project metadata from assets
    metadata = {}
    for key, value in data.copy().items():
        if not isinstance(value, list):
            print("Separating project metadata: %s" % key)
            metadata[key] = data.pop(key)

    _filter = {"type": "project"}

    document = io.find_one(_filter)
    if document is None:
        print("'%s' not found, creating.." % project_name)
        _id = create_project(project_name)

        document = io.find_one({"_id": _id})

    print("Updating project data..")
    for key, value in metadata.items():
        document["data"][key] = value

    io.replace_one(_filter, document)

    print("Updating assets..")
    added = list()
    updated = list()
    missing = list()
    for silo, assets in data.items():
        for asset in assets:

            _filter = {
                "name": asset["name"],
                "type": "asset",
            }

            asset_doc = io.find_one(_filter)

            if asset_doc is None:
                asset["silo"] = silo
                missing.append(asset)
                continue

            for key, value in asset.items():
                asset_doc["data"][key] = value

                if key not in asset_doc["data"]:
                    added.append("%s.%s: %s" % (asset["name"], key, value))

                elif asset_doc["data"][key] != value:
                    updated.append("%s.%s: %s -> %s" % (asset["name"],
                                                        key,
                                                        asset_doc["data"][key],
                                                        value))

            io.replace_one(_filter, asset_doc)

    for data in missing:
        print("+ added %s" % data["name"])

        create_asset(
            name=data.pop("name"),
            silo=data.pop("silo"),
            data=data,
            parent=document["_id"]
        )

    else:
        print("| nothing missing")

    _report(added, missing)


def _save_config_1_0(project_name, data):
    _filter = {"type": "project"}

    document = io.find_one(_filter)

    config = document["config"]

    config["apps"] = data.get("apps", [])
    config["tasks"] = data.get("tasks", [])
    config["template"].update(data.get("template", {}))
    config["families"] = data.get("families", [])
    config["groups"] = data.get("groups", [])

    schema.validate(document)

    io.replace_one(_filter, document)


def _report(added, updated):
    if added:
        print("+ added:")
        print("\n".join(" - %s" % item for item in added))
    else:
        print("| nothing added")

    if updated:
        print("+ updated:")
        print("\n".join("  %s" % item for item in updated))
    else:
        print("| already up to date")


def _read(root, name):
    fname = os.path.join(root, ".%s.toml" % name)

    try:
        with open(fname) as f:
            data = toml.load(f)
    except IOError:
        raise

    return data


def _write(root, name, data):
    fname = os.path.join(root, ".%s.toml" % name)

    try:
        with open(fname, "w") as f:
            toml.dump(data, f)
            schema.validate(data)
    except IOError:
        raise

    return data


def _cli():
    import argparse

    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument("--silo",
                        help="Optional container of silos",
                        action="append",
                        default=["assets", "film"])
    parser.add_argument("--silo-parent", help="Optional silo silo_parent")
    parser.add_argument("--init",
                        action="store_true",
                        help="Start a new project")
    parser.add_argument("--save",
                        action="store_true",
                        help="Save inventory from disk to database")
    parser.add_argument("--load",
                        nargs="?",
                        default=False,
                        help="Load inventory from database to disk")
    parser.add_argument("--ls",
                        action="store_true",
                        help="List all projects in database")
    parser.add_argument("--extract",
                        action="store_true",
                        help="Generate config and inventory "
                             "from assets already on disk.")
    parser.add_argument("--overwrite",
                        action="store_true",
                        help="Overwrite exitsing assets on upload")
    parser.add_argument("--upload",
                        action="store_true",
                        help="Upload generated project to database.")
    parser.add_argument("--root", help="Absolute path to project.")

    kwargs = parser.parse_args()

    root = kwargs.root or os.getcwd()
    name = kwargs.load or os.path.basename(root)

    if any([kwargs.load,
            kwargs.save,
            kwargs.upload,
            kwargs.init,
            kwargs.ls]) or kwargs.load is None:
        os.environ["AVALON_PROJECT"] = name
        io.install()

    if kwargs.init:
        config, inventory = init(name)
        _write(root, "config", config)
        _write(root, "inventory", inventory)
        print("Success!")

    elif kwargs.load or kwargs.load is None:
        config, inventory = load(name)
        _write(root, "config", config)
        _write(root, "inventory", inventory)
        print("Success!")

    elif kwargs.save:
        inventory = _read(root, "inventory")
        config = _read(root, "config")
        save(name, config, inventory)
        print("Successfully saved to %s" % os.getenv("AVALON_MONGO"))

    elif kwargs.ls:
        msg = "Projects in database:"
        for name in ls():
            msg += "\n- {0}".format(name)
        print(msg)

    else:
        print(__doc__)


if __name__ == '__main__':
    try:
        _cli()
    except Exception as e:
        print(e)
        sys.exit(1)
