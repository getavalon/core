import os
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true",
                    help="Enable debug-mode")
parser.add_argument("--creator", action="store_true",
                    help="Launch Instance Creator in standalone mode")
parser.add_argument("--loader", action="store_true",
                    help="Launch Asset Loader in standalone mode")
parser.add_argument("--root",
                    help="Absolute path to root directory of assets")

args = parser.parse_args()

if args.creator:
    from .tools import instance_creator

    def creator(name, family, use_selection):
        print(json.dumps({
            "name": name,
            "family": family,
            "use_selection": use_selection
        }, indent=4))

    instance_creator.show(creator=creator,
                          debug=args.debug)

if args.loader:
    from .tools import asset_loader

    def loader(name):
        print(json.dumps({
            "name": name
        }, indent=4))

    print("Using current working directory.")
    asset_loader.show(root=os.getcwd(),
                      loader=loader,
                      debug=args.debug)
