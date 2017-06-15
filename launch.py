import os

from mindbender.tools import lib as tool_lib
import mindbender.tools.projectmanager as tool
import mindbender.io as io

# Initialize project environment
os.environ["MINDBENDER_PROJECT"] = "testproject"

# Note: The project must have "silos" and "tasks" in its
# configuration in the database.

io.install()
io.activate_project("spiderman")

with tool_lib.application() as application:
    tool.show()
