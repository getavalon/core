import os
import subprocess

from avalon import api, io
from avalon.tools import publish
import pyblish.api
import avalon.photoshop
from avalon.vendor.bottle import route, template, run


@route("/")
def index():
    return template(os.path.join(os.path.dirname(__file__), "index.html"))


def _show(module_name):
    cmd = """
from avalon import api, io
from avalon.tools import {0}
import avalon.photoshop
io.install()
api.register_host(avalon.photoshop)
{0}.show()
"""

    # Need to start a separate process in order for the window to appear ontop
    # of Photoshop.
    subprocess.Popen(["python", "-c", cmd.format(module_name)])


@route("/context_route")
def context_route():
    _show("contextmanager")

    # Required return statement.
    return "nothing"


@route("/workfiles_route")
def workfiles_route():
    _show("workfiles")

    # Required return statement.
    return "nothing"


@route("/creator_route")
def creator_route():
    _show("creator")

    # Required return statement.
    return "nothing"


@route("/loader_route")
def loader_route():
    _show("loader")

    # Required return statement.
    return "nothing"


@route("/publish_route")
def publish_route():

    guis = pyblish.api.registered_guis()
    if guis and guis[0] == "pyblish_lite":
        _show("publish")
    else:
        # Pyblish-QML appears ontop of Photoshop, so we dont need to subprocess
        # it.
        io.install()
        api.register_host(avalon.photoshop)
        publish.show()

    # Required return statement.
    return "nothing"


@route("/manage_route")
def manage_route():
    _show("sceneinventory")

    # Required return statement.
    return "nothing"


if __name__ == "__main__":
    run(host="localhost", port=5000)
