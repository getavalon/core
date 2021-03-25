import os
import importlib
import logging
if os.environ.get("PYPE_ROOT"):
    from pype.api import Anatomy
else:
    Anatomy = None

log = logging.getLogger(__name__)


# `find_config` from `pipeline` but use environment variable
def find_config():
    log.info("Finding configuration for project..")

    config = os.environ["AVALON_CONFIG"]

    if not config:
        raise EnvironmentError(
            "No configuration found in "
            "the project nor environment"
        )

    log.info("Found %s, loading.." % config)
    return importlib.import_module(config)


class RegisteredRoots:
    """Where root for different project may be registered.

    This is used only in Library loader tool when `on_copy` is triggered.
    """
    roots_per_project = {}

    @classmethod
    def register_root(cls, project_name, root):
        cls.roots_per_project[project_name] = root

    @classmethod
    def registered_root(cls, project_name):
        if project_name not in cls.roots_per_project:
            root = None
            if Anatomy:
                root = Anatomy(project_name).roots
            cls.roots_per_project[project_name] = root

        return cls.roots_per_project[project_name]
