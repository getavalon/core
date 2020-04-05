import os
import json
from functools import partial

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


def create_entity(name, project, entity_type, parent):
    print(
        "Creating new entity:\nProject: {}\nEntity Name: {}".format(
            json.dumps(project, sort_keys=True, indent=4),
            name
        )
    )

    # There are no asset type in Avalon, so we take the first available type.
    asset_type = gazu.asset.all_asset_types()[0]

    functions = {
        "asset": partial(gazu.asset.new_asset, project, asset_type, name),
        "episode": partial(gazu.shot.new_episode, project, name),
        "sequence": partial(
            gazu.shot.new_sequence, project, name, episode=parent
        ),
        "shot": partial(gazu.shot.new_shot, project, parent, name)
    }

    return functions[entity_type]()


def get_entity(avalon_entity, project, entity_type, parent=None):
    modules = {
        "asset": gazu.asset.all_assets_for_project,
        "episode": gazu.shot.all_episodes_for_project,
        "sequence": gazu.shot.all_sequences_for_project,
        "shot": gazu.shot.all_shots_for_project
    }

    cgwire_entity = None
    for entity in modules[entity_type](project):
        # Search for existing asset with id.
        if entity["data"].get("avalon_id", "") == str(avalon_entity["_id"]):
            print("Found existing {} by id.".format(entity_type))
            cgwire_entity = entity

        # Search for existing asset with label/name.
        name = avalon_entity["data"].get("label", avalon_entity["name"])
        if entity["name"] == name:
            print("Found existing {} by label/name.".format(entity_type))
            cgwire_entity = entity

    if cgwire_entity is None:
        cgwire_entity = create_entity(
            avalon_entity["name"], project, entity_type, parent
        )

    return cgwire_entity


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


def update_entity(avalon_entity, project, entity_type, parent=None):

    # Update project.
    if entity_type == "project":
        return update_project(avalon_entity)

    # Get cgwire entity.
    cgwire_entity = get_entity(avalon_entity, project, entity_type, parent)

    # Update task data.
    if entity_type in ["asset", "shot"]:
        task_types = {x["name"]: x for x in gazu.task.all_task_types()}
        for task_name in avalon_entity["data"].get("tasks", []):
            gazu.task.new_task(
                cgwire_entity, task_types[task_name.title()], name=task_name
            )
        avalon_entity["data"].pop("tasks", None)

    # Update data.
    data = json.loads(json_util.dumps(avalon_entity["data"]))
    data["avalon_id"] = str(avalon_entity["_id"])

    cgwire_entity.update(
        {
            "data": data,
            "name": avalon_entity["data"].get("label", avalon_entity["name"])
        }
    )

    # Update cgwire_entity.
    modules = {
        "asset": gazu.asset.update_asset,
        "episode": gazu.shot.update_episode,
        "sequence": gazu.shot.update_sequence,
        "shot": gazu.shot.update_shot
    }
    modules[entity_type](cgwire_entity)

    return cgwire_entity


def get_visual_child_ids(database, asset, children):
    for child in database.find({"data.visualParent": asset["_id"]}):
        children.append(child["_id"])
        return get_visual_child_ids(database, child, children)
    return children


def get_visual_children(database, asset):
    ids = get_visual_child_ids(database, asset, [])
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
        cgwire_project = update_entity(
            db[name].find_one({"type": "project"}), None, "project"
        )
        for asset in db[name].find({"type": "asset"}):
            if silo_mapping[asset["silo"]] == "asset":
                update_entity(asset, cgwire_project, "asset")

            if silo_mapping[asset["silo"]] == "shot":
                # If the asset has a visual parent skip.
                if asset["data"].get("visualParent", None):
                    print("Skipping {} due to visual parent.".format(asset))
                    continue

                # Query visual children for hierarchy.
                children = get_visual_children(db[name], asset)

                # One visual child == sequence.
                if len(children) == 1:
                    cgwire_sequence = update_entity(
                        asset, cgwire_project, "sequence"
                    )
                    update_entity(
                        children[0], cgwire_project, "shot", cgwire_sequence
                    )

                # Two visual children == episode/sequence.
                if len(children) == 2:
                    cgwire_episode = update_entity(
                        asset, cgwire_project, "episode"
                    )
                    cgwire_sequence = update_entity(
                        children[0], cgwire_project, "sequence", cgwire_episode
                    )
                    update_entity(
                        children[1], cgwire_project, "shot", cgwire_sequence
                    )
