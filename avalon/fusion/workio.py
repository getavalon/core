"""Host API required Work Files tool"""
import sys
import os


def file_extensions():
    return [".comp"]


def has_unsaved_changes():
    from avalon.fusion.pipeline import get_current_comp

    comp = get_current_comp()
    return comp.GetAttrs()["COMPB_Modified"]


def save_file(filepath):
    from avalon.fusion.pipeline import get_current_comp

    comp = get_current_comp()
    comp.Save(filepath)


def open_file(filepath):
    # Hack to get fusion, see avalon.fusion.pipeline.get_current_comp()
    fusion = getattr(sys.modules["__main__"], "fusion", None)

    return fusion.LoadComp(filepath)


def current_file():
    from avalon.fusion.pipeline import get_current_comp

    comp = get_current_comp()
    current_filepath = comp.GetAttrs()["COMPS_FileName"]
    if not current_filepath:
        return None

    return current_filepath


def work_root():
    from avalon import Session

    work_dir = Session["AVALON_WORKDIR"]
    scene_dir = Session.get("AVALON_SCENEDIR")
    if scene_dir:
        return os.path.join(work_dir, scene_dir)
    else:
        return work_dir
