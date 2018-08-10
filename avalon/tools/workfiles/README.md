# Workfiles App

The Workfiles app facilitates easy saving, creation and launching of work files.

The current supported hosts are:

- Maya

The app is available inside hosts via. the ```Avalon > Work Files``` menu.

## Enabling Workfiles on launch

By default the Workfiles app will not launch on startup, so it has to be explicitly enabled in a config.

```python
workfiles.show(
    os.path.join(
        cmds.workspace(query=True, rootDirectory=True),
        cmds.workspace(fileRuleEntry="scene")
    )
)
```

## Naming Files

Workfiles app enables user to easily save and create new work files.

The user is presented with a two parameters; ```version``` and ```comment```. The name of the work file is determined from a template.

### ```Next Available Version```

Will search for the next version number that is not in use.

## Templates

The default template for work files is ```{task[name]}_v{version:0>4}<_{comment}>```. Launching Maya on an animation task and creating a version 1 will result in ```animation_v0001.ma```. Adding "blocking" to the optional comment input will result in ```animation_v0001_blocking.ma```.

This template can be customized per project with the ```workfile``` template.

There are other variables to customize the template with:

```python
{
    "project": project,  # The project data from the database.
    "asset": asset, # The asset data from the database.
    "task": {
        "label": label,  # Label of task chosen.
        "name": name  # Sanitize version of the label.
    },
    "user": user,  # Name of the user on the machine.
    "version": version,  # Chosen version of the user.
    "comment": comment,  # Chosen comment of the user.
}
```

### Optional template groups

The default template contains an optional template group ```<_{comment}>```. If any template group (```{comment}```) within angle bracket ```<>``` does not exist, the whole optional group is discarded.
