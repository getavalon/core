"""Used for scripting

These are used in other scripts and mostly require explicit input,
such as which specific nodes they apply to.

For interactive use, see :mod:`interactive.py`

"""

from maya import cmds

from .. import io, api


def reset_frame_range():
    """Set frame range to current asset"""
    # Set FPS first
    fps = {15: 'game',
           24: 'film',
           25: 'pal',
           30: 'ntsc',
           48: 'show',
           50: 'palf',
           60: 'ntscf',
           23.98: '23.976fps',
           23.976: '23.976fps',
           29.97: '29.97fps',
           47.952: '47.952fps',
           47.95: '47.952fps',
           59.94: '59.94fps',
           44100: '44100fps',
           48000: '48000fps'
           }.get(float(api.Session.get("AVALON_FPS", 25)), "pal")

    cmds.currentUnit(time=fps)

    # Set frame start/end
    asset_name = api.Session["AVALON_ASSET"]
    asset = io.find_one({"name": asset_name, "type": "asset"})

    frame_start = asset["data"].get("frameStart")
    frame_end = asset["data"].get("frameEnd")
    # Backwards compatibility
    if frame_start is None or frame_end is None:
        frame_start = asset["data"].get("edit_in")
        frame_end = asset["data"].get("edit_out")

    if frame_start is None or frame_end is None:
        cmds.warning("No edit information found for %s" % asset_name)
        return

    handles = asset["data"].get("handles") or 0
    handle_start = asset["data"].get("handleStart")
    if handle_start is None:
        handle_start = handles

    handle_end = asset["data"].get("handleEnd")
    if handle_end is None:
        handle_end = handles

    frame_start -= int(handle_start)
    frame_end += int(handle_end)

    cmds.playbackOptions(minTime=frame_start)
    cmds.playbackOptions(maxTime=frame_end)
    cmds.playbackOptions(animationStartTime=frame_start)
    cmds.playbackOptions(animationEndTime=frame_end)
    cmds.playbackOptions(minTime=frame_start)
    cmds.playbackOptions(maxTime=frame_end)
    cmds.currentTime(frame_start)

    cmds.setAttr("defaultRenderGlobals.startFrame", frame_start)
    cmds.setAttr("defaultRenderGlobals.endFrame", frame_end)


def _resolution_from_document(doc):
    if not doc or "data" not in doc:
        print("Entered document is not valid. \"{}\"".format(str(doc)))
        return None

    resolution_width = doc["data"].get("resolutionWidth")
    resolution_height = doc["data"].get("resolutionHeight")
    # Backwards compatibility
    if resolution_width is None or resolution_height is None:
        resolution_width = doc["data"].get("resolution_width")
        resolution_height = doc["data"].get("resolution_height")

    # Make sure both width and heigh are set
    if resolution_width is None or resolution_height is None:
        cmds.warning(
            "No resolution information found for \"{}\"".format(doc["name"])
        )
        return None

    return int(resolution_width), int(resolution_height)


def reset_resolution():
    # Default values
    resolution_width = 1920
    resolution_height = 1080

    # Get resolution from asset
    asset_name = api.Session["AVALON_ASSET"]
    asset_doc = io.find_one({"name": asset_name, "type": "asset"})
    resolution = _resolution_from_document(asset_doc)
    # Try get resolution from project
    if resolution is None:
        # TODO go through visualParents
        print((
            "Asset \"{}\" does not have set resolution."
            " Trying to get resolution from project"
        ).format(asset_name))
        project_doc = io.find_one({"type": "project"})
        resolution = _resolution_from_document(project_doc)

    if resolution is None:
        msg = "Using default resolution {}x{}"
    else:
        resolution_width, resolution_height = resolution
        msg = "Setting resolution to {}x{}"

    print(msg.format(resolution_width, resolution_height))

    cmds.setAttr("defaultResolution.width", resolution_width)
    cmds.setAttr("defaultResolution.height", resolution_height)
