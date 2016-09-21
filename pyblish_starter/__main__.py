import os
import json
import types
import argparse
from . import pipeline

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


# Produce standalone host
def root():
    return os.getcwd()


def loader(asset, version=-1, representation=None):
    print(json.dumps({
        "asset": asset,
        "version": version,
        "representation": representation
    }, indent=4))

    return "my_asset"


def creator(name, family):
    print(json.dumps({
        "name": name,
        "family": family,
    }, indent=4))

host = types.ModuleType("Standalone")
host.root = root
host.loader = loader
host.creator = creator

pipeline.register_host(host)


if args.creator:
    from .tools import instance_creator
    instance_creator.show(debug=args.debug)

if args.loader:
    from .tools import asset_loader
    asset_loader.show(debug=args.debug)
