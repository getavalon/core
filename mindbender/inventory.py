"""Utility script for updating database with configuration files

Until assets are created entirely in the database, this script
provides a bridge between the file-based project inventory and configuration.

- Migrating an old project:
    $ python -m mindbender.inventory --extract
    $ python -m mindbender.inventory --upload

- Managing an existing project:
    1. Run `python -m mindbender.inventory --load`
    2. Update the .inventory.toml or .config.toml
    3. Run `python -m mindbender.inventory --save`

"""

import os
import sys
import copy
import json

from mindbender import schema, io
from mindbender.vendor import toml

self = sys.modules[__name__]
self.collection = None


DEFAULTS = {
    "config": {
        "schema": "mindbender-core:config-1.0",
        "apps": [
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
            {"name": "modeling"},
            {"name": "animation"},
            {"name": "rigging"},
            {"name": "lookdev"},
            {"name": "layout"},
        ],
        "template": {
            "work":
                "{root}/{project}/{silo}/{asset}/work/"
                "{task}/{user}/{app}",
            "publish":
                "{root}/{project}/{silo}/{asset}/publish/"
                "{subset}/v{version:0>3}/{subset}.{representation}"
        }
    },
    "inventory": {
        "schema": "mindbender-core:inventory-1.0",
        "assets": [
            {
                "name": "Default asset 1"
            },
            {
                "name": "Default asset 2"
            }
        ],
        "film": [
            {
                "name": "Default shot 1",
                "edit_in": 1000,
                "edit_out": 1143
            },
            {
                "name": "Default shot 2",
                "edit_in": 1000,
                "edit_out": 1081
            },
        ]
    }
}


def _save_inventory_1_0(project_name, data):
    metadata = {}
    for key, value in data.items():
        if not isinstance(value, list):
            metadata[key] = data.pop(key)

    document = io.find_one({"type": "project", "name": project_name})

    if document is None:
        print("'%s' not found, creating.." % project_name)
        _project = {
            "schema": "mindbender-core:project-2.0",
            "type": "project",
            "name": project_name,
            "data": dict(),
            "config": {
                "template": {},
                "tasks": [],
                "apps": [],
                "copy": {}
            },
            "parent": None,
        }

        schema.validate(_project)
        _id = io.insert_one(_project).inserted_id

        document = io.find_one({"_id": _id})

    print("Updating project data..")
    for key, value in metadata.items():
        document["data"][key] = value

    io.save(document)

    print("Updating assets..")
    added = list()
    updated = list()
    missing = list()
    for silo, assets in data.items():
        for asset in assets:
            asset_doc = io.find_one({
                "name": asset["name"],
                "parent": document["_id"]
            })

            if asset_doc is None:
                asset["silo"] = silo
                asset["data"] = dict(asset)
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

            io.save(asset_doc)

    for data in missing:
        print("+ added %s" % data["name"])

        asset = {
            "schema": "mindbender-core:asset-2.0",
            "name": data["name"],
            "silo": data["silo"],
            "parent": document["_id"],
            "type": "asset",
            "data": data
        }

        schema.validate(asset)
        io.insert_one(asset)

    else:
        print("| nothing missing")

    _report(added, missing)


def _save_config_1_0(project_name, data):
    document = io.find_one({"type": "project", "name": project_name})
    config = document["config"]

    added = list()
    updated = list()

    config["apps"] = data.get("apps", [])
    config["tasks"] = data.get("tasks", [])
    config["template"].update(data.get("template", {}))

    schema.validate(document)

    io.save(document)

    _report(added, updated)


def save(name, config, inventory):
    """Write config and inventory to database from `root`"""
    print("Saving .inventory.toml and .config.toml..")

    config = copy.deepcopy(config)
    inventory = copy.deepcopy(inventory)

    handlers = {
        "mindbender-core:inventory-1.0": _save_inventory_1_0,
        "mindbender-core:config-1.0": _save_config_1_0
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
            handler(name, data)

    print("Success!")


def load(name):
    """Write config and inventory to `root` from database

    Arguments:
        name (str): Project name

    """

    print("Loading .inventory.toml and .config.toml..")

    project = io.find_one({"type": "project", "name": name})

    if project is None:
        print("No project found, loading defaults..")
        config = {}
        inventory = DEFAULTS["inventory"]

    else:
        config = project["config"]
        inventory = {"schema": "mindbender-core:inventory-1.0"}
        for asset in io.find({"type": "asset", "parent": project["_id"]}):
            silo = asset["silo"]
            data = asset["data"]

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


def _parse_bat(root):
    """Return environment variables from .bat files

    Handles:
        Integers:
            $ set MINDBENDER_VARIABLE=1000
        Strings:
            $ set MINDBENDER_VARIABLE="String"
        Plain
            $ set MINDBENDER_VARIABLE=plain


    """

    name = os.path.basename(root)
    dirname = os.path.dirname(root)
    data = dict()

    try:
        with open(os.path.join(dirname, name + ".bat")) as f:
            for line in f:
                if not line.startswith("set MINDBENDER_"):
                    continue

                key, value = line.rstrip().split("=")
                key = key[len("set MINDBENDER_"):].lower()

                # Automatically convert to proper datatype
                try:
                    value = json.loads(value)
                    value = int(value)
                except ValueError:
                    # Value wasn't an integer
                    pass

                data[key] = value

    except IOError:
        pass

    return data


def extract(root, silos):
    """Parse a given project and produce a JSON file of its contents

    Arguments:
        root (str): Absolute path to a file-based project

    """

    name = os.path.basename(root)

    print("Generating project.json..")

    project_obj = {
        "schema": "mindbender-core:project-2.0",
        "name": name,
        "type": "project",
        "data": {},
        "config": {
            "schema": "mindbender-core:config-1.0",
            "apps": copy.deepcopy(DEFAULTS["config"]["apps"]),
            "tasks": copy.deepcopy(DEFAULTS["config"]["tasks"]),
            "template": copy.deepcopy(DEFAULTS["config"]["template"]),
            "copy": {},
        },
        "children": list(),
    }

    # Parse .bat file for environment variables
    project_obj.update(_parse_bat(root))

    for silo in silos:
        for asset in _dirs(os.path.join(root, *silo.split("/"))):
            asset_obj = {
                "schema": "mindbender-core:asset-2.0",
                "type": "asset",
                "name": os.path.basename(asset),
                "silo": silo,
                "data": {},
                "children": list(),
            }

            schema.validate(asset_obj)

            asset_obj.update(_parse_bat(asset))

            project_obj["children"].append(asset_obj)

            for subset in _dirs(os.path.join(asset, "publish")):
                subset_obj = {
                    "schema": "mindbender-core:subset-2.0",
                    "name": os.path.basename(subset),
                    "type": "subset",
                    "data": {},
                    "children": list(),
                }

                schema.validate(subset_obj)

                asset_obj["children"].append(subset_obj)

                for version in _dirs(subset):
                    try:
                        with open(os.path.join(version,
                                               ".metadata.json")) as f:
                            metadata = json.load(f)
                    except IOError:
                        continue

                    try:
                        number = int(os.path.basename(version)[1:])
                    except ValueError:
                        # Directory not compatible with pipeline
                        # E.g. 001_mySpecialVersion
                        continue

                    try:
                        version_obj = {
                            "schema": "mindbender-core:version-2.0",
                            "type": "version",
                            "name": number,
                            "data": {
                                "families": metadata["families"],
                                "author": metadata["author"],
                                "source": metadata["source"],
                                "time": metadata["time"],
                            },
                            "children": list(),
                        }
                    except KeyError:
                        # Metadata not compatible with pipeline
                        continue

                    schema.validate(version_obj)

                    subset_obj["children"].append(version_obj)

                    for representation in metadata["representations"]:
                        representation_obj = {
                            "schema": "mindbender-core:representation-2.0",
                            "type": "representation",
                            "name": representation["format"].strip("."),
                            "data": {
                                "label": representation["format"].strip("."),
                            },
                            "children": list(),
                        }

                        schema.validate(representation_obj)

                        version_obj["children"].append(representation_obj)

    with open(os.path.join(root, "project.json"), "w") as f:
        json.dump(project_obj, f, indent=4)

    print("Successfully generated %s" % os.path.join(root, "project.json"))


def upload(root, overwrite=False):
    fname = os.path.join(root, "project.json")
    print("Uploading %s" % os.path.basename(root))

    try:
        with open(fname) as f:
            project = json.load(f)
    except IOError:
        raise IOError("No project.json found.")

    def _upload_recursive(parent, children):
        for child in children:
            grandchildren = child.pop("children")
            child["parent"] = parent

            document = io.find_one({
                key: child[key]
                for key in ("parent",
                            "type",
                            "name")
            })

            if document is None:
                _id = io.insert_one(child).inserted_id
                print("+ {0[type]}: '{0[name]}'".format(child))
            elif overwrite:
                _id = document["_id"]
                document.update(child)
                io.save(document)
                print("~ {0[type]}: '{0[name]}'".format(child))
            else:
                _id = document["_id"]
                print("| {0[type]}: '{0[name]}'..".format(child))

            _upload_recursive(_id, grandchildren)

    _upload_recursive(None, [project])

    print("Successfully uploaded %s" % fname)


def status(root):
    """Print configuration and inventory from `root`"""
    print(__doc__)


def _dirs(path):
    try:
        for base, dirs, files in os.walk(path):
            return list(
                os.path.join(base, dirname) for dirname in dirs
            )
    except IOError:
        return list()

    return list()


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
            data = toml.dump(data, f)
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
    parser.add_argument("--save",
                        action="store_true",
                        help="Save inventory from disk to database")
    parser.add_argument("--load",
                        action="store_true",
                        help="Load inventory from database to disk")
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
    name = os.path.basename(root)

    if kwargs.load:
        io.install()
        config, inventory = load(name)
        _write(root, "config", config)
        _write(root, "inventory", inventory)
        print("Success!")

    elif kwargs.save:
        io.install()
        inventory = _read(root, "inventory")
        config = _read(root, "config")
        save(name, config, inventory)
        print("Success!")

    elif kwargs.extract:
        extract(root=root, silos=kwargs.silo)
        print("Success!")

    elif kwargs.upload:
        io.install()
        upload(root=root, overwrite=kwargs.overwrite)
        print("Success!")

    else:
        status(root=root)
        print("Success!")


if __name__ == '__main__':
    sys.exit(_cli())
