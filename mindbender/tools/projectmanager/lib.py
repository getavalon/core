"""Utility script for updating database with configuration files

Until assets are created entirely in the database, this script
provides a bridge between the file-based project inventory and configuration.

- Migrating an old project:
    $ python -m mindbender.inventory --extract --silo-parent=f02_prod
    $ python -m mindbender.inventory --upload

- Managing an existing project:
    1. Run `python -m mindbender.inventory --load`
    2. Update the .inventory.toml or .config.toml
    3. Run `python -m mindbender.inventory --save`

"""


from mindbender import schema, io


def create_asset(data):
    """Create asset

    Requires:
        {"name": "uniquecode",
         "label": "Nice readable name",
         "silo": "assets"}

     Optional:
        {"data": {}}
    """

    data = data.copy()

    project = io.find_one({"type": "project"})
    if project is None:
        raise RuntimeError("Project must exist prior to creating assets")

    # Link to parent by id if provided, otherwise parent to the project
    parent = data.pop("parent") or project['_id']

    asset = {
        "schema": "mindbender-core:asset-2.0",
        "name": data.pop("name"),
        "silo": data.pop("silo"),
        "parent": parent,
        "type": "asset",
        "data": data
    }

    # Asset *must* have a name and silo
    assert asset['name'], "Asset has no name"
    assert asset['silo'], "Asset has no silo"

    # Ensure it has a unique name
    asset_doc = io.find_one({
        "name": asset['name'],
        "type": "asset",
    })
    if asset_doc is not None:
        raise RuntimeError("Asset named {} already "
                           "exists.".format(asset['name']))

    schema.validate(asset)
    io.insert_one(asset)


def list_project_tasks():
    """List the projec task types available in the current project"""
    project = io.find_one({"type": "project"})
    return [task['name'] for task in project['config']['tasks']]


# def create_project(project_name, metadata):
#     # Activate afterwards
#     io.activate_project(project_name)
#
#     document = io.find_one({"type": "project"})
#     if document is None:
#         print("'%s' not found, creating.." % project_name)
#         _project = {
#             "schema": "mindbender-core:project-2.0",
#             "type": "project",
#             "name": project_name,
#             "data": dict(),
#             "config": {
#                 "template": {},
#                 "tasks": [],
#                 "apps": [],
#                 "copy": {}
#             },
#             "parent": None,
#         }
#
#         _id = io.insert_one(_project).inserted_id
#
#         schema.validate(_project)
#         document = io.find_one({"_id": _id})
#
#     print("Updating project data..")
#     for key, value in metadata.items():
#         document["data"][key] = value