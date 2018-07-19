# Workfiles App

The Workfiles app facilitates easy creation and launching of work files.

The current supported hosts are:

- Maya
- Nuke

## Enabling Workfiles on launch

By default the Workfiles app will not launch, so it has to be explicitly enabled.

### ```.toml``` Applications

```toml
workfiles_app = true
workfiles_dir = "scenes"
```

| Variable | Description
| --- | ---
| workfiles_app | Boolean value to enable the Workfiles app on launch.
| workfiles_dir | Initially the Workfiles app search and present work files from the ```application_dir```. Some applications like Maya has a subdirectory where work files are stored. ```workfiles_dir``` facilitates adding to ```application_dir```.


### Action Applications

```python
from avalon.tools import workfiles
work_file = workfiles.show(root=cwd, executable=executable)
```

| Argument | Description
| --- | ---
| root | The directory to search and present work files from.
| executable | The application executable to create work files from.

## New Work Files

Workfiles app enables user to easily create new work files, without having to launch a GUI host.

The user is presented with a single parameter; ```version```. The name of the work file is determined from a template.

## Templates

The default template for work files is ```{task[name]}_v{version:0>4}```. Launching Maya on an animation task and creating a version 1 will result in ```animation_v0001.ma```.

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
    "version": version,  # Chosen version of the user.
    "user": user  # Name of the user on the machine.
}
```

## Hosts

Workfiles is available inside hosts via. the ```Avalon > Work Files``` menu.
