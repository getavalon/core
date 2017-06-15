
from .app import (
    show,
)


def cli(args):
    import argparse
    from ... import io
    parser = argparse.ArgumentParser()
    parser.add_argument("project")

    args = parser.parse_args(args)
    project = args.project

    io.install()
    io.activate_project(project)
    show()


__all__ = [
    "show",
]
