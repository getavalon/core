# Storyboard Pro Integration

## Setup

The easiest way to setup for using Toon Boom Storyboard Pro is to use the built-in launch:

```
python -c "import avalon.storyboardpro;avalon.storyboardpro.launch("path/to/storyboardpro/executable")"
```

Communication with Storyboard Pro happens with a server/client relationship where the server is in the Python process and the client is in the Storyboard Pro process. Messages between Python and Storyboard Pro are required to be dictionaries, which are serialized to strings:
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

Storyboard Pro integration cannot create a menu entry on launch. Users need to executate the provided script to get the menu entry. Script Editor > `avalon.js` > Run Script > `start`.

### Work files

Because Storyboard Pro projects are directories, this integration uses `.zip` as work file extension. Internally the project directories are stored under `[User]/.avalon/storyboardpro`. Whenever the user saves the scene file, the integration zips up the project directory and moves it to the Avalon project path. Zipping and moving happens in the background.

### Show Workfiles on launch

You can show the Workfiles app when Storyboard Pro launches by setting environment variable `AVALON_TOONBOOM_WORKFILES_ON_LAUNCH=1`.

## Developing

To send from Python to Storyboard Pro you can use the exposed method:
```python
from avalon import toonboom
func = """function hello(person)
{
  return ("Hello " + person + "!");
}
hello
"""
print(toonboom.send({"function": func, "args": ["Python"]})["result"])
```
NOTE: Its important to declare the function at the end of the function string. You can have multiple functions within your function string, but the function declared at the end is what gets executed.

To send a function with multiple arguments its best to declare the arguments within the function:
```python
from avalon import toonboom
func = """function hello(args)
{
  var greeting = args[0];
  var person = args[1];
  return (greeting + " " + person + "!");
}
hello
"""
print(toonboom.send({"function": func, "args": ["Hello", "Python"]})["result"])
```

### Scene Save
Instead of sending a request to Storyboard Pro with `scene.saveAll` please use:
```python
from avalon import toonboom
toonboom.save_scene()
```

<details>
  <summary>Click to expand for details on scene save.</summary>

  Because Avalon tools does not deal well with folders for a single entity like a Storyboard Pro scene, this integration has implemented to use zip files to encapsulate the Storyboard Pro scene folders. This is done with a background watcher for when the `.xstage` file is changed, at which point a request is sent to zip up the Harmony scene folder and move from the local to remote storage.

  This does come with an edge case where if you send `scene.saveAll` to Storyboard Pro, two request will be sent back; the reply to `scene.saveAll` and the request to zip and move the scene folder. To prevent this a boolean has been implemented to the background watcher; `app.avalon_on_file_changed`, enable and disable to zip and move.
</details>
