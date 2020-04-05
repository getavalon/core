import os
import json

import pymongo
from bson import json_util

# Try/Except for prevent error in import testing.
try:
    import gazu
except ImportError:
    pass


def get_project(avalon_project):
    for project in gazu.project.all_projects():
        if project["data"].get("avalon_id", "") == str(avalon_project["_id"]):
            print("Found existing project by id. Project: {}".format(project))
            return project

    print(
        "Creating new project:\nProject Name: {}".format(
            avalon_project["name"]
        )
    )
    return gazu.project.new_project(avalon_project["name"])


def get_entity(project, avalon_asset, cgwire_type):
    modules = {
        "asset": gazu.asset.all_assets_for_project,
        "episode": gazu.shot.all_episodes_for_project,
        "sequence": gazu.shot.all_sequences_for_project,
        "shot": gazu.shot.all_shots_for_project
    }

    for entity in modules[cgwire_type](project):
        # Search for existing asset with id.
        if entity["data"].get("avalon_id", "") == str(avalon_asset["_id"]):
            print("Found existing {} by id.".format(cgwire_type))
            return entity

        # Search for existing asset with label/name.
        name = avalon_asset["data"].get("label", avalon_asset["name"])
        if entity["name"] == name:
            print("Found existing {} by label/name.".format(cgwire_type))
            return entity


def get_asset(cgwire_project, avalon_asset):
    cgwire_asset = get_entity(cgwire_project, avalon_asset, "asset")

    if cgwire_asset is None:
        print(
            "Creating new asset:\nProject: {}\nAsset Type: {}"
            "\nAsset Name: {}".format(
                json.dumps(cgwire_project, sort_keys=True, indent=4),
                gazu.asset.all_asset_types()[0],
                avalon_asset["name"]
            )
        )
        # There are no asset type in Avalon, so we take the first
        # available asset type.
        cgwire_asset = gazu.asset.new_asset(
            cgwire_project,
            gazu.asset.all_asset_types()[0],
            avalon_asset["name"]
        )

    return cgwire_asset


def get_episode(cgwire_project, avalon_asset):
    cgwire_episode = get_entity(cgwire_project, avalon_asset, "episode")

    if cgwire_episode is None:
        print(
            "Creating new episode:\nProject: {}\nEpisode Name: {}".format(
                json.dumps(cgwire_project, sort_keys=True, indent=4),
                avalon_asset["name"]
            )
        )
        cgwire_episode = gazu.shot.new_episode(
            cgwire_project,
            avalon_asset["name"]
        )

    return cgwire_episode


def get_sequence(cgwire_project, avalon_asset, episode=None):
    cgwire_sequence = get_entity(cgwire_project, avalon_asset, "sequence")

    if cgwire_sequence is None:
        print(
            "Creating new sequence:\nProject: {}\nName: {}"
            "\nEpisode: {}".format(
                json.dumps(cgwire_project, sort_keys=True, indent=4),
                avalon_asset["name"],
                json.dumps(episode, sort_keys=True, indent=4)
            )
        )
        cgwire_sequence = gazu.shot.new_sequence(
            cgwire_project,
            avalon_asset["name"],
            episode=episode
        )

    return cgwire_sequence


def get_shot(cgwire_project, cgwire_sequence, avalon_asset):
    cgwire_shot = get_entity(cgwire_project, avalon_asset, "shot")

    if cgwire_shot is None:
        print(
            "Creating new shot:\nProject: {}\nSequence: {}"
            "\nShot Name: {}".format(
                json.dumps(cgwire_project, sort_keys=True, indent=4),
                json.dumps(cgwire_sequence, sort_keys=True, indent=4),
                avalon_asset["name"]
            )
        )
        cgwire_shot = gazu.shot.new_shot(
            cgwire_project,
            cgwire_sequence,
            avalon_asset["name"]
        )

    return cgwire_shot


def update_project(avalon_project):
    """Update CGWire project with Avalon project data.

    Args:
        project (dict): Avalon project.
    """
    cgwire_project = get_project(avalon_project)

    # Update task data.
    task_types = [x["name"] for x in gazu.task.all_task_types()]
    for task in avalon_project["config"]["tasks"]:
        if task["name"].title() in task_types:
            continue
        gazu.task.new_task_type(task["name"].title())

    avalon_project["config"].pop("tasks")

    # Update project data.
    data = json.loads(json_util.dumps(avalon_project["data"]))
    data.update(avalon_project["config"])
    data["avalon_id"] = str(avalon_project["_id"])

    cgwire_project.update({
        "code": avalon_project["name"].replace(" ", "_").lower(),
        "data": data,
        "name": avalon_project["name"]
    })
    gazu.project.update_project(cgwire_project)

    return cgwire_project


def update_entity(avalon_entity, cgwire_entity, cgwire_type):
    # Update task data.
    if cgwire_type in ["asset", "shot"]:
        task_types = {x["name"]: x for x in gazu.task.all_task_types()}
        for task_name in avalon_entity["data"].get("tasks", []):
            gazu.task.new_task(
                cgwire_entity, task_types[task_name.title()], name=task_name
            )
        avalon_entity["data"].pop("tasks", None)

    # Update data.
    data = json.loads(json_util.dumps(avalon_entity["data"]))
    data["avalon_id"] = str(avalon_entity["_id"])

    cgwire_entity.update({
        "data": data,
        "name": avalon_entity["data"].get("label", avalon_entity["name"])
    })

    # Update cgwire_entity.
    modules = {
        "asset": gazu.asset.update_asset,
        "episode": gazu.shot.update_episode,
        "sequence": gazu.shot.update_sequence,
        "shot": gazu.shot.update_shot
    }
    modules[cgwire_type](cgwire_entity)


def update_asset(cgwire_project, avalon_asset):
    cgwire_asset = get_asset(cgwire_project, avalon_asset)

    # Update data.
    update_entity(avalon_asset, cgwire_asset, "asset")

    return cgwire_asset


def update_episode(cgwire_project, avalon_asset):
    cgwire_episode = get_episode(cgwire_project, avalon_asset)

    # Update data.
    update_entity(avalon_asset, cgwire_episode, "episode")

    return cgwire_episode


def update_sequence(cgwire_project, avalon_asset, episode=None):
    cgwire_sequence = get_sequence(cgwire_project, avalon_asset, episode)

    # Update data.
    update_entity(avalon_asset, cgwire_sequence, "sequence")

    return cgwire_sequence


def update_shot(cgwire_project, cgwire_sequence, avalon_asset):
    cgwire_shot = get_shot(cgwire_project, cgwire_sequence, avalon_asset)

    # Update asset data.
    update_entity(avalon_asset, cgwire_shot, "shot")

    return cgwire_shot


def get_visual_child_ids(database, asset, children=[]):
    for child in database.find({"data.visualParent": asset["_id"]}):
        children.append(child["_id"])
        return get_visual_child_ids(database, child, children)
    return children


def get_visual_children(database, asset):
    ids = get_visual_child_ids(database, asset)
    children = []
    for id in ids:
        child = database.find_one({"_id": id})
        if child:
            children.append(child)
    return children


def full_sync():
    gazu.client.set_host("http://127.0.0.1/api")
    gazu.log_in("admin@example.com", "mysecretpassword")

    # Mapping.
    silo_mapping = {"film": "shot", "assets": "asset"}

    # Collect all projects data in Mongo.
    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]

    for name in db.collection_names():
        cgwire_project = update_project(db[name].find_one({"type": "project"}))
        for asset in db[name].find({"type": "asset"}):
            if silo_mapping[asset["silo"]] == "asset":
                update_asset(cgwire_project, asset)

            if silo_mapping[asset["silo"]] == "shot":
                # If the asset has a visual parent skip.
                if asset["data"].get("visualParent", None):
                    print("Skipping {} due to visual parent.".format(asset))
                    continue

                # Query visual children for hierarchy.
                children = get_visual_children(db[name], asset)

                # One visual child == sequence.
                if len(children) == 1:
                    cgwire_sequence = update_sequence(
                        cgwire_project, asset
                    )
                    update_shot(cgwire_project, cgwire_sequence, children[0])

                # Two visual children == episode/sequence.
                if len(children) == 2:
                    cgwire_episode = update_episode(
                        cgwire_project, asset
                    )
                    cgwire_sequence = update_sequence(
                        cgwire_project,
                        children[0],
                        episode=cgwire_episode
                    )
                    update_shot(cgwire_project, cgwire_sequence, children[1])
