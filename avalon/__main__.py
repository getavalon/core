import argparse

from . import pipeline, version


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true", help=(
        "Print version and exit"))
    parser.add_argument("--root",
                        help="Absolute path to root directory of assets")
    parser.add_argument("--creator", action="store_true",
                        help="Launch Instance Creator in standalone mode")
    parser.add_argument("--loader", action="store_true",
                        help="Launch Asset Loader in standalone mode")
    parser.add_argument("--sceneinventory", action="store_true",
                        help="Launch Scene Inventory in standalone mode")
    parser.add_argument("--projectmanager", action="store_true",
                        help="Launch Manager in standalone mode")

    args, unknown = parser.parse_known_args()
    host = pipeline.debug_host()
    pipeline.register_host(host)

    if args.version:
        print("avalon==%s" % version.version)
        exit(0)

    elif args.creator:
        from .tools import creator
        creator.show(debug=True)

    elif args.loader:
        from .tools import loader
        loader.show(debug=True)

    elif args.sceneinventory:
        from .tools import sceneinventory
        sceneinventory.show(debug=True)

    elif args.projectmanager:
        from .tools import projectmanager
        projectmanager.cli(unknown)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
