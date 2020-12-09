import os
import re
import json
import contextlib
import uuid
import tempfile

import pyblish.api
from .. import api, io
from . import lib
from ..pipeline import AVALON_CONTAINER_ID


METADATA_SECTION = "avalon"
SECTION_NAME_CONTEXT = "context"
SECTION_NAME_INSTANCES = "instances"
SECTION_NAME_CONTAINERS = "containers"


def install():
    """Install Maya-specific functionality of avalon-core.

    This function is called automatically on calling `api.install(maya)`.

    """
    io.install()

    # Create workdir folder if does not exist yet
    workdir = api.Session["AVALON_WORKDIR"]
    if not os.path.exists(workdir):
        os.makedirs(workdir)

    pyblish.api.register_host("tvpaint")


def uninstall():
    """Uninstall TVPaint-specific functionality of avalon-core.

    This function is called automatically on calling `api.uninstall()`.

    """

    pyblish.api.deregister_host("tvpaint")


def containerise(
    name, namespace, layer_ids, context, loader, current_containers=None
):
    """Add new container to metadata.

    Args:
        name (str): Container name.
        namespace (str): Container namespace.
        layer_ids (list): List of layer that were loaded and belongs to the
            container.
        current_containers (list): Preloaded containers. Should be used only
            on update/switch when containers were modified durring the process.

    Returns:
        dict: Container data stored to workfile metadata.
    """

    container_data = {
        "schema": "avalon-core:container-2.0",
        "id": AVALON_CONTAINER_ID,
        "members": layer_ids,
        "name": name,
        "namespace": namespace,
        "loader": str(loader),
        "representation": str(context["representation"]["_id"])
    }
    if current_containers is None:
        current_containers = ls()

    # Add container to containers list
    current_containers.append(container_data)

    # Store data to metadata
    write_workfile_metadata(SECTION_NAME_CONTAINERS, current_containers)

    return container_data


@contextlib.contextmanager
def maintained_selection():
    # TODO implement logic
    try:
        yield
    finally:
        pass


def get_workfile_metadata(metadata_key, default=None):
    """Read metadata for specific key from current project workfile.

    Pipeline use function to store loaded and created instances within keys
    stored in `SECTION_NAME_INSTANCES` and `SECTION_NAME_CONTAINERS`
    constants.

    Args:
        metadata_key (str): Key defying which key should read. It is expected
            value contain json serializable string.
    """
    if default is None:
        default = []
    output_file = tempfile.NamedTemporaryFile(
        mode="w", prefix="a_tvp_", suffix=".txt", delete=False
    )
    output_file.close()

    output_filepath = output_file.name.replace("\\", "/")
    george_script = (
        "output_path = \"{}\"\n"
        "tv_readprojectstring \"{}\" \"{}\" \"[]\"\n"
        "tv_writetextfile \"strict\" \"append\" '\"'output_path'\"' result"
    ).format(output_filepath, METADATA_SECTION, metadata_key)
    lib.execute_george_through_file(george_script)

    with open(output_filepath, "r") as stream:
        json_string = stream.read()
    # Replace quotes plaholders with their values
    json_string = (
        json_string
        .replace("{__sq__}", "'")
        .replace("{__dq__}", "\"")
    )
    os.remove(output_filepath)
    if json_string:
        return json.loads(json_string)
    return default


def write_workfile_metadata(metadata_key, value):
    """Write metadata for specific key into current project workfile.

    George script has specific way how to work with quotes which should be
    solved automatically with this function.

    Args:
        metadata_key (str): Key defying under which key value will be stored.
        value (dict,list,str): Data to store they must be json serializable.
    """
    if isinstance(value, (dict, list)):
        value = json.dumps(value)

    if not value:
        value = ""

    # Handle quotes in dumped json string
    # - replace single and double quotes with placeholders
    value = (
        value
        .replace("'", "{__sq__}")
        .replace("\"", "{__dq__}")
    )

    george_script = (
        "tv_writeprojectstring \"{}\" \"{}\" \"{}\""
    ).format(METADATA_SECTION, metadata_key, value)
    return lib.execute_george_through_file(george_script)


def get_current_workfile_context():
    """Return context in which was workfile saved."""
    return get_workfile_metadata(SECTION_NAME_CONTEXT, {})


def save_current_workfile_context(context):
    """Save context which was used to create a workfile."""
    return write_workfile_metadata(SECTION_NAME_CONTEXT, context)


def remove_instance(instance):
    """Remove instance from current workfile metadata."""
    current_instances = get_workfile_metadata(SECTION_NAME_INSTANCES)
    instance_id = instance.get("uuid")
    found_idx = None
    if instance_id:
        for idx, _inst in enumerate(current_instances):
            if _inst["uuid"] == instance_id:
                found_idx = idx
                break

    if found_idx is None:
        return
    current_instances.pop(found_idx)
    _write_instances(current_instances)


def list_instances():
    """List all created instances from current workfile."""
    return get_workfile_metadata(SECTION_NAME_INSTANCES)


def _write_instances(data):
    return write_workfile_metadata(SECTION_NAME_INSTANCES, data)


def ls():
    return get_workfile_metadata(SECTION_NAME_CONTAINERS)


class Creator(api.Creator):
    def __init__(self, *args, **kwargs):
        super(Creator, self).__init__(*args, **kwargs)
        # Add unified identifier created with `uuid` module
        self.data["uuid"] = str(uuid.uuid4())

    @staticmethod
    def are_instances_same(instance_1, instance_2):
        """Compare instances but skip keys with unique values.

        During compare are skiped keys that will be 100% sure
        different on new instance, like "id".

        Returns:
            bool: True if instances are same.
        """
        if (
            not isinstance(instance_1, dict)
            or not isinstance(instance_2, dict)
        ):
            return instance_1 == instance_2

        checked_keys = set()
        checked_keys.add("id")
        for key, value in instance_1.items():
            if key not in checked_keys:
                if key not in instance_2:
                    return False
                if value != instance_2[key]:
                    return False
                checked_keys.add(key)

        for key in instance_2.keys():
            if key not in checked_keys:
                return False
        return True

    def write_instances(self, data):
        self.log.debug(
            "Storing instance data to workfile. {}".format(str(data))
        )
        return _write_instances(data)

    def process(self):
        data = list_instances()
        data.append(self.data)
        self.write_instances(data)


class Loader(api.Loader):
    hosts = ["tvpaint"]

    @staticmethod
    def layer_ids_from_container(container):
        if "members" not in container and "objectName" in container:
            # Backwards compatibility
            layer_ids_str = container.get("objectName")
            return [
                int(layer_id) for layer_id in layer_ids_str.split("|")
            ]
        return container["members"]

    def get_unique_layer_name(self, asset_name, name):
        """Layer name with counter as suffix.

        Find higher 3 digit suffix from all layer names in scene matching regex
        `{asset_name}_{name}_{suffix}`. Higher 3 digit suffix is used
        as base for next number if scene does not contain layer matching regex
        `0` is used ase base.

        Args:
            asset_name (str): Name of subset's parent asset document.
            name (str): Name of loaded subset.

        Returns:
            (str): `{asset_name}_{name}_{higher suffix + 1}`
        """
        layer_name_base = "{}_{}".format(asset_name, name)

        counter_regex = re.compile(r"_(\d{3})$")

        higher_counter = 0
        for layer in lib.layers_data():
            layer_name = layer["name"]
            if not layer_name.startswith(layer_name_base):
                continue
            number_subpart = layer_name[len(layer_name_base):]
            groups = counter_regex.findall(number_subpart)
            if len(groups) != 1:
                continue

            counter = int(groups[0])
            if counter > higher_counter:
                higher_counter = counter
                continue

        return "{}_{:0>3d}".format(layer_name_base, higher_counter + 1)
