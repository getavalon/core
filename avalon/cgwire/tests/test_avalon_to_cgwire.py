import sys
import os
import contextlib

from nose.tools import with_setup

import avalon.io
import avalon.inventory
import avalon.cgwire.cgwire
import pymongo

# Try/Except for prevent error in import testing.
try:
    import gazu
except ImportError:
    pass


self = sys.modules[__name__]


os.environ["AVALON_PROJECT"] = "batman"
os.environ["AVALON_ASSET"] = "bruce"
os.environ["AVALON_SILO"] = "assets"
avalon.io.install()

project_name = "batman"

os.environ["CGWIRE_HOST"] = "http://127.0.0.1/api"
os.environ["CGWIRE_USERNAME"] = "admin@example.com"
os.environ["CGWIRE_PASSWORD"] = "mysecretpassword"
gazu.client.set_host(os.environ["CGWIRE_HOST"])
gazu.log_in(os.environ["CGWIRE_USERNAME"], os.environ["CGWIRE_PASSWORD"])


@contextlib.contextmanager
def setup():
    for project in gazu.project.all_projects():
        for shot in gazu.shot.all_shots_for_project(project):
            gazu.shot.remove_shot(shot, force=True)
        for asset in gazu.asset.all_assets_for_project(project):
            gazu.asset.remove_asset(asset, force=True)

        for sequence in gazu.shot.all_sequences_for_project(project):
            gazu.shot.remove_sequence(sequence)

        for episode in gazu.shot.all_episodes_for_project(project):
            gazu.shot.remove_episode(episode)

        # CGWire projects needs to be closed before deletion.
        gazu.project.close_project(project)
        gazu.project.remove_project(project, force=True)

    avalon.io.delete_many({})


@with_setup(setup)
def test_project_sync():
    """Syncing project from Avalon to CGWire works."""

    project_id = avalon.inventory.create_project(project_name)
    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    avalon_project = db[project_name].find_one({"_id": project_id})

    avalon.cgwire.cgwire.full_sync()

    # There should only be one project in CGWire at this point.
    cgwire_project = gazu.project.all_projects()[0]

    assert avalon_project["name"] == cgwire_project["name"]
    assert str(avalon_project["_id"]) == cgwire_project["data"]["avalon_id"]

    task_types = [x["name"] for x in gazu.task.all_task_types()]
    missing_task_types = []
    for task in avalon_project["config"]["tasks"]:
        if task["name"].title() not in task_types:
            missing_task_types.append(task)

    assert not missing_task_types


@with_setup(setup)
def test_asset_sync():
    """Syncing asset from Avalon to CGWire works."""

    project_id = avalon.inventory.create_project(project_name)
    asset_id = avalon.inventory.create_asset(
        "Bruce", "assets", {"tasks": ["modeling"]}, project_id
    )

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    avalon_asset = db[project_name].find_one({"_id": asset_id})

    avalon.cgwire.cgwire.full_sync()

    # There should only be one project in CGWire at this point.
    cgwire_project = gazu.project.all_projects()[0]

    # There should only be one asset in CGWire at this point.
    cgwire_asset = gazu.asset.all_assets_for_project(cgwire_project)[0]

    assert avalon_asset["name"] == cgwire_asset["name"]
    assert str(avalon_asset["_id"]) == cgwire_asset["data"]["avalon_id"]

    cgwire_tasks = [
        task["name"] for task in gazu.task.all_tasks_for_asset(cgwire_asset)
    ]
    assert avalon_asset["data"]["tasks"] == cgwire_tasks


@with_setup(setup)
def test_sequence_sync():
    """Syncing sequence from Avalon to CGWire works."""

    project_id = avalon.inventory.create_project(project_name)
    sequence_id = avalon.inventory.create_asset(
        "sequence", "film", {}, project_id
    )
    shot_id = avalon.inventory.create_asset(
        "shot",
        "film",
        {"tasks": ["layout"], "visualParent": sequence_id},
        project_id
    )

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    avalon_sequence = db[project_name].find_one({"_id": sequence_id})
    avalon_shot = db[project_name].find_one({"_id": shot_id})

    avalon.cgwire.cgwire.full_sync()

    # There should only be one project in CGWire at this point.
    cgwire_project = gazu.project.all_projects()[0]

    # There should only be one sequence in CGWire at this point.
    cgwire_sequence = gazu.shot.all_sequences_for_project(cgwire_project)[0]

    assert avalon_sequence["name"] == cgwire_sequence["name"]
    assert str(avalon_sequence["_id"]) == cgwire_sequence["data"]["avalon_id"]

    # There should only be one shot in CGWire at this point.
    cgwire_shot = gazu.shot.all_shots_for_project(cgwire_project)[0]

    assert avalon_shot["name"] == cgwire_shot["name"]
    assert str(avalon_shot["_id"]) == cgwire_shot["data"]["avalon_id"]

    cgwire_tasks = [
        task["name"] for task in gazu.task.all_tasks_for_shot(cgwire_shot)
    ]
    assert avalon_shot["data"]["tasks"] == cgwire_tasks


@with_setup(setup)
def test_episode_sync():
    """Syncing episode from Avalon to CGWire works."""

    project_id = avalon.inventory.create_project(project_name)
    episode_id = avalon.inventory.create_asset(
        "episode", "film", {}, project_id
    )
    sequence_id = avalon.inventory.create_asset(
        "sequence", "film", {"visualParent": episode_id}, project_id
    )
    shot_id = avalon.inventory.create_asset(
        "shot",
        "film",
        {"tasks": ["layout"], "visualParent": sequence_id},
        project_id
    )

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    avalon_episode = db[project_name].find_one({"_id": episode_id})
    avalon_sequence = db[project_name].find_one({"_id": sequence_id})
    avalon_shot = db[project_name].find_one({"_id": shot_id})

    avalon.cgwire.cgwire.full_sync()

    # There should only be one project in CGWire at this point.
    cgwire_project = gazu.project.all_projects()[0]

    # There should only be one episode in CGWire at this point.
    cgwire_episode = gazu.shot.all_episodes_for_project(cgwire_project)[0]

    assert avalon_episode["name"] == cgwire_episode["name"]
    assert str(avalon_episode["_id"]) == cgwire_episode["data"]["avalon_id"]

    # There should only be one sequence in CGWire at this point.
    cgwire_sequence = gazu.shot.all_sequences_for_project(cgwire_project)[0]

    assert avalon_sequence["name"] == cgwire_sequence["name"]
    assert str(avalon_sequence["_id"]) == cgwire_sequence["data"]["avalon_id"]

    # There should only be one shot in CGWire at this point.
    cgwire_shot = gazu.shot.all_shots_for_project(cgwire_project)[0]

    assert avalon_shot["name"] == cgwire_shot["name"]
    assert str(avalon_shot["_id"]) == cgwire_shot["data"]["avalon_id"]

    cgwire_tasks = [
        task["name"] for task in gazu.task.all_tasks_for_shot(cgwire_shot)
    ]
    assert avalon_shot["data"]["tasks"] == cgwire_tasks
