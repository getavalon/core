import os
import sys
import copy
import shutil
import tempfile
import subprocess
import contextlib

from avalon import io, inventory, schema
from avalon.vendor import toml

from nose.tools import (
    assert_equals,
    assert_raises,
    with_setup,
)

PROJECT_NAME = "hulk"

self = sys.modules[__name__]
self._project = {
    "schema": "avalon-core:project-2.0",
    "type": "project",
    "name": PROJECT_NAME,
    "config": {
        "template": {},
        "tasks": [],
        "apps": [],
        "copy": {}
    },
    "data": {},
}
self._config = {
    "schema": "avalon-core:config-1.0",
    "apps": [
        {"name": "app1"},
        {"name": "app2"},
    ],
    "tasks": [
        {"name": "task1"},
        {"name": "task2"},
    ],
    "template": {
        "work":
            "{root}/{project}/{silo}/{asset}/work/"
            "{task}/{user}/{app}",
        "publish":
            "{root}/{project}/{silo}/{asset}/publish/"
            "{subset}/v{version:0>3}/{subset}.{representation}"
    },
    "copy": {}
}

self._inventory = {
    "schema": "avalon-core:inventory-1.0",
    "assets": [
        {"name": "asset1"},
    ],
    "film": [
        {"name": "shot1"},
    ]
}


def setup():
    assert_equals.__self__.maxDiff = None
    os.environ["AVALON_PROJECT"] = PROJECT_NAME

    # Fill in other required keys for the Session schema to avoid warnings
    # todo: figure out why these are actually required in the schema here
    for key in ["AVALON_PROJECTS",
                "AVALON_ASSET",
                "AVALON_SILO",
                "AVALON_CONFIG"]:
        os.environ[key] = "placeholder"

    io.install()
    self._tempdir = tempfile.mkdtemp()


def teardown():
    shutil.rmtree(self._tempdir)
    io.delete_many({})  # Faster than `drop()`


@contextlib.contextmanager
def clean():
    io.delete_many({})


@with_setup(clean)
def test_init():
    """Initialising a new project yields defaults"""

    test_project = tempfile.mkdtemp(dir=self._tempdir)

    inventory_fname = os.path.join(test_project, ".inventory.toml")
    config_fname = os.path.join(test_project, ".config.toml")

    assert 0 == subprocess.call([
        sys.executable, "-u", "-m", "avalon.inventory", "--init"
    ], cwd=test_project)

    assert os.path.isfile(inventory_fname), ".inventory.toml not found"
    assert os.path.isfile(config_fname), ".config.toml not found"

    with open(inventory_fname) as f:
        inventory_dict = toml.load(f)
        assert_equals(inventory_dict, inventory.DEFAULTS["inventory"])

    with open(config_fname) as f:
        config_dict = toml.load(f)
        assert_equals(config_dict, inventory.DEFAULTS["config"])


@with_setup(clean)
def test_save():
    """Saving works well under normal circumstances"""
    config_ = {
        "schema": "avalon-core:config-1.0",
        "apps": [
            {"name": "app1"},
            {"name": "app2"},
        ],
        "tasks": [
            {"name": "task1"},
            {"name": "task2"},
        ],
        "template": {
            "work":
                "{root}/{project}/{silo}/{asset}/work/"
                "{task}/{user}/{app}",
            "publish":
                "{root}/{project}/{silo}/{asset}/publish/"
                "{subset}/v{version:0>3}/{subset}.{representation}"
        },
        "copy": {}
    }

    inventory_ = {
        "schema": "avalon-core:inventory-1.0",
        "assets": [
            {"name": "asset1"},
            {"name": "asset2"}
        ],
        "film": [
            {"name": "shot1"},
            {"name": "shot2"},
        ]
    }

    schema.validate(config_)
    schema.validate(inventory_)

    _id = io.insert_one(self._project).inserted_id
    project = io.find_one({"_id": _id})

    assert_equals(project["config"], self._project["config"])

    inventory.save(
        name=self._project["name"],
        config=config_,
        inventory=inventory_
    )

    project = io.find_one({"_id": _id})
    config_.pop("schema")
    assert_equals(project["config"], config_)

    for asset in inventory_["assets"]:
        assert io.find_one({
            "type": "asset",
            "parent": project["_id"],
            "name": asset["name"]
        })


@with_setup(clean)
def test_save_bad_inventory():
    """Invalid inventory raises schema error"""
    config_ = {"bad": "yes"}
    inventory_ = {"wrong": True}

    assert_raises(
        schema.SchemaError,
        inventory.save,
        name=self._project["name"],
        config=config_,
        inventory=inventory_
    )


@with_setup(clean)
def test_save_bad_inventory2():
    """Invalid inventory with proper schema raises validation error"""
    config_ = {"schema": "avalon-core:config-1.0"}
    inventory_ = {"schema": "avalon-core:inventory-1.0"}

    assert_raises(
        schema.ValidationError,
        inventory.save,
        name=self._project["name"],
        config=config_,
        inventory=inventory_
    )


@with_setup(clean)
def test_save_idempotent():
    """Saving many times doesn't duplicate assets"""

    inventory.save(
        name=self._project["name"],
        config=self._config,
        inventory=self._inventory
    )

    assert_equals(io.find({"type": "asset"}).count(),
                  len(self._inventory["assets"]) +
                  len(self._inventory["film"]))

    inventory.save(
        name=self._project["name"],
        config=self._config,
        inventory=self._inventory
    )

    assert_equals(io.find({"type": "asset"}).count(),
                  len(self._inventory["assets"]) +
                  len(self._inventory["film"]))


@with_setup(clean)
def test_list_projects():
    """Listing projects in database"""

    inventory.save(
        name=self._project["name"],
        config=self._config,
        inventory=self._inventory
    )

    return_code = subprocess.call(
        [
            sys.executable,
            "-u",
            "-m",
            "avalon.inventory",
            "--ls"
        ],
        cwd=tempfile.mkdtemp(dir=self._tempdir)
    )

    assert 0 == return_code


@with_setup(clean)
def test_cli_load_no_project():
    """Loading a project via CLI that does not exist throws an error"""

    assert 0 != subprocess.call([
        sys.executable, "-u", "-m", "avalon.inventory", "--load"
    ], cwd=self._tempdir)


@with_setup(clean)
def test_load_no_project():
    """Loading a project that does not exist throws an error"""

    assert_raises(Exception, inventory.load, PROJECT_NAME)


@with_setup(clean)
def test_cli_load_overwrite():
    """Loading when an existing inventory exists quietly overwrites it"""

    test_project = tempfile.mkdtemp(dir=self._tempdir)

    subprocess.call([
        sys.executable, "-u", "-m", "avalon.inventory", "--init"
    ], cwd=test_project)

    subprocess.call([
        sys.executable, "-u", "-m", "avalon.inventory", "--save"
    ], cwd=test_project)

    assert 0 == subprocess.call([
        sys.executable, "-u", "-m", "avalon.inventory", "--load"
    ], cwd=test_project)

    assert 0 == subprocess.call([
        sys.executable, "-u", "-m", "avalon.inventory", "--load"
    ], cwd=test_project)


@with_setup(clean)
def test_cli_load_by_name():
    """Load project by name"""

    inventory.save(
        name=self._project["name"],
        config=self._config,
        inventory=self._inventory
    )

    return_code = subprocess.call(
        [
            sys.executable,
            "-u",
            "-m",
            "avalon.inventory",
            "--load",
            self._project["name"]
        ],
        cwd=tempfile.mkdtemp(dir=self._tempdir)
    )

    assert 0 == return_code


@with_setup(clean)
def test_cli_save():
    """Saving uploads inventory to database"""
    with open(os.path.join(self._tempdir, ".inventory.toml"), "w") as f:
        toml.dump(self._inventory, f)

    with open(os.path.join(self._tempdir, ".config.toml"), "w") as f:
        toml.dump(self._config, f)

    assert 0 == subprocess.call([
        sys.executable, "-u", "-m", "avalon.inventory", "--save"
    ], cwd=self._tempdir)


@with_setup(clean)
def test_load():
    """Loading produces compatible results for saving"""

    inventory.save(
        name=self._project["name"],
        config=self._config,
        inventory=self._inventory
    )

    _config, _inventory = inventory.load(PROJECT_NAME)
    schema.validate(_config)
    schema.validate(_inventory)

    inventory.save(
        name=self._project["name"],
        config=_config,
        inventory=_inventory
    )

    _config, _inventory = inventory.load(PROJECT_NAME)
    schema.validate(_config)
    schema.validate(_inventory)


@with_setup(clean)
def test_save_project_data():
    """The inventory can take (plain) project data as well"""

    inventory_ = copy.deepcopy(self._inventory)
    inventory_["key"] = "value"
    inventory_["key2"] = "value2"

    inventory.save(
        name=self._project["name"],
        config=self._config,
        inventory=inventory_
    )

    project = io.find_one({"type": "project", "name": PROJECT_NAME})
    assert_equals(project["data"]["key"], "value")
    assert_equals(project["data"]["key2"], "value2")


@with_setup(clean)
def test_save_asset_data():
    """The inventory can take asset data as well"""

    inventory_ = copy.deepcopy(self._inventory)

    asset = inventory_["assets"][0]
    asset.update({
        "key": "value"
    })

    inventory.save(
        name=self._project["name"],
        config=self._config,
        inventory=inventory_
    )

    asset = io.find_one({"type": "asset", "name": asset["name"]})
    print(asset)
    assert_equals(asset["data"]["key"], "value")


@with_setup(clean)
def test_save_toml():
    text = """\
schema = "avalon-core:config-1.0"
[[apps]]
name = "maya2016"
label = "Autodesk Maya 2016"

[[apps]]
name = "nuke10"
label = "The Foundry Nuke 10.0"

[[tasks]]
name = "model"

[[tasks]]
name = "render"

[[tasks]]
name = "animation"

[[tasks]]
name = "rig"

[[tasks]]
name = "lookdev"

[[tasks]]
name = "layout"

[template]
work = "{root}/{project}/f02_prod/{silo}"
publish = "{root}/{project}/f02_prod/{silo}"

[copy]"""

    config_ = toml.loads(text)
    schema.validate(config_)

    inventory.save(
        name=self._project["name"],
        config=config_,
        inventory=self._inventory
    )


@with_setup(clean)
def test_save_new_project():

    # No project exists
    inventory.save(
        name=self._project["name"],
        config=self._config,
        inventory=self._inventory
    )


@with_setup(clean)
def test_asset_name():
    """Assets with spaces and other special characters are invalid"""

    invalid = {}
    inventory_ = copy.deepcopy(self._inventory)
    inventory_["assets"].append(invalid)

    for name in ("mixedCaseOk",
                 "lowercaseok",
                 "underscore_ok"):
        invalid["name"] = name

        inventory.save(
            name=self._project["name"],
            config=self._config,
            inventory=inventory_
        )

    for name in ("spaces not ok",
                 "special~characters$not^ok",
                 "dash-not-ok"):
        invalid["name"] = name

        assert_raises(
            schema.ValidationError,
            inventory.save,
            name=self._project["name"],
            config=self._config,
            inventory=inventory_
        )
