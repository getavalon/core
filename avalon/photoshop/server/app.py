import os

from avalon import api, photoshop
from avalon.tools import (
    contextmanager,
    workfiles,
    creator,
    loader,
    publish,
    sceneinventory,
    projectmanager
)
from avalon.vendor.bottle import route, template, run


api.install(photoshop)


@route("/")
def index():
    return template(os.path.join(os.path.dirname(__file__), "index.html"))


@route("/context_route")
def context_route():
    contextmanager.show()

    # Required return statement.
    return "nothing"


@route("/workfiles_route")
def workfiles_route():
    workfiles.show()

    # Required return statement.
    return "nothing"


@route("/creator_route")
def creator_route():
    creator.show()

    # Required return statement.
    return "nothing"


@route("/loader_route")
def loader_route():
    loader.show()

    # Required return statement.
    return "nothing"


@route("/publish_route")
def publish_route():
    publish.show()

    # Required return statement.
    return "nothing"


@route("/manage_route")
def manage_route():
    sceneinventory.show()

    # Required return statement.
    return "nothing"


@route("/project_manager_route")
def project_manager_route():
    projectmanager.show()

    # Required return statement.
    return "nothing"


def start_server():
    run(host="localhost", port=5000)


if __name__ == "__main__":
    start_server()
