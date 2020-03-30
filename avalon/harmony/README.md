# Photoshop Integration

## Setup

The easiest way to setup for using Toon Boom Harmony is to use the built-in launch:

```
python -c "import avalon.harmony;avalon.harmony.launch("path/to/harmony/executable")"
```

The server/Harmony relationship looks like this:
```
+------------+
|            |
|   Python   |
|   Process  |
|            |
| +--------+ |
| |        | |
| |  Main  | |
| | Thread | |
| |        | |
| +----^---+ |
|     ||     |
|     ||     |
| +---v----+ |     +---------+
| |        | |     |         |
| | Server +-------> Harmony |
| | Thread <-------+ Process |
| |        | |     |         |
| +--------+ |     +---------+
+------------+
```

## Usage

The integration creates an `Avalon` menu entry where all Avalon related tools are located.

**NOTE: Menu creation can be temperamental. The best way is to launch Harmony and do nothing else until Harmony is fully launched.**

### Work files

Because Harmony projects are directories, this integration uses `.zip` as work file extension. Internally the project directories are stored under `[User]/.avalon/harmony`. Whenever the user saves the `.xstage` file, the integration zips up the project directory and move it to the Avalon project path. Zipping and moving happens in the background.

### Show Workfiles on launch

You can show the Workfiles app when Harmony launches by setting environment variable `AVALON_HARMONY_WORKFILES_ON_LAUNCH=1`.

## Developing
### Plugin Examples
These plugins were made with the [polly config](https://github.com/mindbender-studio/config).

#### Creator Plugin
```python
from avalon import harmony


class CreateComposite(harmony.Creator):
    """Composite node for publish."""

    name = "compositeDefault"
    label = "Composite"
    family = "mindbender.imagesequence"

    def __init__(self, *args, **kwargs):
        super(CreateComposite, self).__init__(*args, **kwargs)
```

#### Collector Plugin
```python
import pyblish.api
from avalon import harmony


class CollectInstances(pyblish.api.ContextPlugin):
    """Gather instances by nodes metadata.

    This collector takes into account assets that are associated with
    a composite node and marked with a unique identifier;

    Identifier:
        id (str): "pyblish.avalon.instance"
    """

    label = "Instances"
    order = pyblish.api.CollectorOrder
    hosts = ["harmony"]

    def process(self, context):
        nodes = harmony.send(
            {"function": "node.getNodes", "args": [["COMPOSITE"]]}
        )["result"]

        for node in nodes:
            data = harmony.read(node)

            # Skip non-tagged nodes.
            if not data:
                continue

            # Skip containers.
            if "container" in data["id"]:
                continue

            instance = context.create_instance(node.split("/")[-1])
            instance.append(node)
            instance.data.update(data)

            # Produce diagnostic message for any graphical
            # user interface interested in visualising it.
            self.log.info("Found: \"%s\" " % instance.data["name"])
```

#### Extractor Plugin
```python
import os

import pyblish.api
from avalon import harmony

import clique


class ExtractImage(pyblish.api.InstancePlugin):
    """Produce a flattened image file from instance.
    This plug-in only takes into account the nodes connected to the composite.
    """
    label = "Extract Image Sequence"
    order = pyblish.api.ExtractorOrder
    hosts = ["harmony"]
    families = ["mindbender.imagesequence"]

    def process(self, instance):
        project_path = harmony.send(
            {"function": "scene.currentProjectPath"}
        )["result"]

        # Store reference for integration
        if "files" not in instance.data:
            instance.data["files"] = list()

        # Store display source node for later.
        display_node = "Top/Display"
        func = """function func(display_node)
        {
            var source_node = null;
            if (node.isLinked(display_node, 0))
            {
                source_node = node.srcNode(display_node, 0);
                node.unlink(display_node, 0);
            }
            return source_node
        }
        func
        """
        display_source_node = harmony.send(
            {"function": func, "args": [display_node]}
        )["result"]

        # Perform extraction
        path = os.path.join(
            os.path.normpath(
                project_path
            ).replace("\\", "/"),
            instance.data["name"]
        )
        if not os.path.exists(path):
            os.makedirs(path)

        render_func = """function frameReady(frame, celImage)
        {{
          var path = "{path}/{filename}" + frame + ".png";
          celImage.imageFileAs(path, "", "PNG4");
        }}
        function func(composite_node)
        {{
            node.link(composite_node, 0, "{display_node}", 0);
            render.frameReady.connect(frameReady);
            render.setRenderDisplay("{display_node}");
            render.renderSceneAll();
            render.frameReady.disconnect(frameReady);
        }}
        func
        """
        restore_func = """function func(args)
        {
            var display_node = args[0];
            var display_source_node = args[1];
            if (node.isLinked(display_node, 0))
            {
                node.unlink(display_node, 0);
            }
            node.link(display_source_node, 0, display_node, 0);
        }
        func
        """

        with harmony.maintained_selection():
            self.log.info("Extracting %s" % str(list(instance)))

            harmony.send(
                {
                    "function": render_func.format(
                        path=path.replace("\\", "/"),
                        filename=os.path.basename(path),
                        display_node=display_node
                    ),
                    "args": [instance[0]]
                }
            )

            # Restore display.
            if display_source_node:
                harmony.send(
                    {
                        "function": restore_func,
                        "args": [display_node, display_source_node]
                    }
                )

        files = os.listdir(path)
        collections, remainder = clique.assemble(files, minimum_items=1)
        assert not remainder, (
            "There shouldn't have been a remainder for '%s': "
            "%s" % (instance[0], remainder)
        )
        assert len(collections) == 1, (
            "There should only be one image sequence in {}. Found: {}".format(
                path, len(collections)
            )
        )

        data = {
            "subset": collections[0].head,
            "isSeries": True,
            "stagingDir": path,
            "files": list(collections[0]),
        }
        instance.data.update(data)

        self.log.info("Extracted {instance} to {path}".format(**locals()))
```


## Resources
- https://github.com/diegogarciahuerta/tk-harmony
- https://github.com/cfourney/OpenHarmony
- [Toon Boom Discord](https://discord.gg/syAjy4H)
- [Toon Boom TD](https://discord.gg/yAjyQtZ)
