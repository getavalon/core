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
                "{root}/{project}/{prefix}{silo}/{asset}/work/"
                "{task}/{user}/{app}",
            "publish":
                "{root}/{project}/{prefix}{silo}/{asset}/publish/"
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


def _update_inventory_1_0(project, inventory):
    document = io.find_one({"type": "project", "name": project})

    if document is None:
        print("'%s' not found, creating.." % project)
        print("Inserting new project %s" % project)
        _id = io.insert_one({
            "type": "project",
            "name": project,
            "parent": None,
            "schema": "mindbender-core:asset-1.0"
        }).inserted_id

        document = io.find_one({"_id": _id})

    added = list()
    updated = list()
    missing = list()
    for silo, assets in inventory.items():
        for name, data in assets.items():
            data = data or {}

            asset = io.find_one({
                "name": name,
                "parent": document["_id"]
            })

            if asset is None:
                data["name"] = name
                data["silo"] = silo
                missing.append(data)
                continue

            for key, value in data.items():
                if key not in asset:
                    asset[key] = value
                    added.append("%s.%s: %s" % (name, key, value))

                elif asset[key] != value:
                    asset[key] = value
                    updated.append("%s.%s: %s -> %s" % (name,
                                                        key,
                                                        asset[key],
                                                        value))

            io.save(asset)

    if missing:
        print("+ added asset(s): %s" % ", ".join([a["name"] for a in missing]))
        io.insert_many([dict({
            "type": "asset",
            "parent": document["_id"],
            "schema": "mindbender-core:asset-1.0"
        }, **asset_) for asset_ in missing])

    else:
        print("| nothing missing")

    _report(added, missing)


def _update_config_1_0(project, config):
    document = io.find_one({"type": "project", "name": project})

    added = list()
    updated = list()

    for key, value in config.get("metadata", {}).items():
        if key not in document:
            added.append("%s.%s: %s" % (project, key, value))
            document[key] = value
        elif document[key] != value:
            updated.append("%s.%s: %s -> %s" % (project,
                                                key,
                                                document[key],
                                                value))
            document[key] = value

    document["apps"] = list(
        dict({"name": key}, **value)
        for key, value in config.get("apps", {}).items()
    )
    document["tasks"] = list(
        dict({"name": key}, **value)
        for key, value in config.get("tasks", {}).items()
    )
    document["template"] = config.get("template", [])

    io.save(document)

    _report(added, updated)


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
        print("ERROR: No %s, using defaults" % name)
        return DEFAULTS[name]

    return data


def save(root=None):
    """Write config and inventory to database from `root`"""
    print("--> Saving .inventory.toml and .config.toml..")

    root = root or os.getcwd()
    project = os.path.basename(root)

    print("Locating project '%s'" % project)

    handlers = {
        "mindbender-core:inventory-1.0": _update_inventory_1_0,
        "mindbender-core:config-1.0": _update_config_1_0
    }

    for fname in ["inventory", "config"]:
        try:
            data = _read(root, fname)

        except (schema.ValidationError,
                schema.SchemaError,
                IndexError,
                toml.TomlDecodeError) as e:
            print(e)
            print("ERROR: Misformatted: '%s'" % root)
            sys.exit(1)

        try:
            schema_ = data.pop("schema", None)
            handler = handlers[schema_]
            handler(project, data)

        except KeyError:
            print("ERROR: Missing handler for "
                  "'%s' (schema: %s)" % (project, schema_))
            sys.exit(1)

    print("Success!")


def load(root=None):
    """Write config and inventory to `root` from database"""
    print("<-- Loading .inventory.toml and .config.toml..")

    root = root or os.getcwd()
    name = os.path.basename(root)

    project_doc = io.find_one({"type": "project", "name": name})

    if project_doc is None:
        print("%s was not found in database." % name)
        return 1

    inventory = {}
    for asset in io.find({"type": "asset", "parent": project_doc["_id"]}):
        silo = asset["silo"]
        if silo not in inventory:
            inventory[silo] = {}

        inventory[silo][asset["name"]] = {
            key: value for key, value in asset.items()
            if key not in (
                "_id",
                "parent",
                "name",
                "schema",
                "type",
                "silo",
                "date",
            )
        } or None

    with open(os.path.join(root, ".inventory.toml"), "w") as f:
        toml.dump(dict({
            "schema": "mindbender-core:inventory-1.0",
        }, **inventory), f)

    with open(os.path.join(root, ".config.toml"), "w") as f:
        toml.dump({
            "schema": "mindbender-core:config-1.0",
            "metadata": {
                key: value for key, value in project_doc.items()
                if key not in (
                    "_id",
                    "schema",
                    "apps",
                    "type",
                    "tasks",
                    "template",
                    "date",
                )
            },
            "apps": {
                item["name"]: {
                    key: value
                    for key, value in item.items()
                    if key != "name"
                }
                for item in project_doc.get(
                    "apps", DEFAULTS["config"]["apps"])
            },
            "tasks": {
                item["name"]: {
                    key: value
                    for key, value in item.items()
                    if key != "name"
                }
                for item in project_doc.get(
                    "tasks", DEFAULTS["config"]["tasks"])
            },
            "template": project_doc.get(
                "template", DEFAULTS["config"]["template"])
        }, f)

    print("Success!")


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


def extract(root=None, prefix=""):
    """Parse a given project and produce a JSON file of its contents

    Arguments:
        root (str): Absolute path to a file-based project

    """

    root = root or os.getcwd()
    name = os.path.basename(root)

    print("Generating project.json..")

    project_obj = {
        "schema": "mindbender-core:project-2.0",
        "name": name,
        "type": "project",
        "apps": copy.deepcopy(DEFAULTS["config"]["apps"]),
        "tasks": copy.deepcopy(DEFAULTS["config"]["tasks"]),
        "template": copy.deepcopy(DEFAULTS["config"]["template"]),
        "children": list(),
    }

    # Account for prefix.
    for key, value in project_obj["template"].copy().items():
        project_obj["template"][key] = value.replace("{prefix}", prefix)

    # Parse .bat file for environment variables
    project_obj.update(_parse_bat(root))

    for silo in ("assets", "film"):
        for asset in _dirs(os.path.join(root, prefix + silo)):
            asset_obj = {
                "schema": "mindbender-core:asset-2.0",
                "name": os.path.basename(asset),
                "silo": silo,
                "type": "asset",
                "children": list(),
            }

            asset_obj.update(_parse_bat(asset))

            project_obj["children"].append(asset_obj)

            for subset in _dirs(os.path.join(asset, "publish")):
                subset_obj = {
                    "schema": "mindbender-core:subset-2.0",
                    "name": os.path.basename(subset),
                    "type": "subset",
                    "children": list(),
                }

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
                            "name": number,
                            "families": metadata["families"],
                            "author": metadata["author"],
                            "source": metadata["source"],
                            "time": metadata["time"],
                            "type": "version",
                            "children": list(),
                        }
                    except KeyError:
                        # Metadata not compatible with pipeline
                        continue

                    subset_obj["children"].append(version_obj)

                    for representation in metadata["representations"]:
                        representation_obj = {
                            "schema": "mindbender-core:representation-2.0",
                            "name": representation["format"].strip("."),
                            "label": representation["format"].strip("."),
                            "type": "representation",
                            "children": list(),
                        }
                        version_obj["children"].append(representation_obj)

    with open(os.path.join(root, "project.json"), "w") as f:
        json.dump(project_obj, f, indent=4)

    print("Successfully generated %s" % os.path.join(root, "project.json"))


def upload(root=None, overwrite=False):
    root = root or os.getcwd()
    fname = os.path.join(root, "project.json")
    print("Uploading %s" % os.path.basename(root))

    try:
        with open(fname) as f:
            project = json.load(f)
    except IOError:
        print("No project.json found.")
        return 1

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
    os.remove(fname)

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


def _cli():
    import argparse

    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument("--silo-prefix",
                        help="Optional silo parent dir.",
                        default="")

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

    if kwargs.load:
        io.install()
        return load(root=kwargs.root)

    elif kwargs.save:
        io.install()
        return save(root=kwargs.root)

    elif kwargs.extract:
        return extract(root=kwargs.root, prefix=kwargs.silo_prefix)

    elif kwargs.upload:
        io.install()
        return upload(root=kwargs.root, overwrite=kwargs.overwrite)

    else:
        return status(root=kwargs.root)


if __name__ == '__main__':
    sys.exit(_cli())
