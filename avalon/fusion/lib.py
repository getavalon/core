import contextlib
from . import pipeline


@contextlib.contextmanager
def maintained_selection():
    comp = pipeline.get_current_comp()
    previous_selection = comp.GetToolList(True).values()
    try:
        yield
    finally:
        flow = comp.CurrentFrame.FlowView
        flow.Select()  # No args equals clearing selection
        if previous_selection:
            for tool in previous_selection:
                flow.Select(tool, True)
