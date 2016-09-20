
if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--load", action="store_true")

    args = parser.parse_args()

    if args.create:
        from .tools import instance_creator
        instance_creator.show(create=lambda *args, **kwargs: None)

    if args.load:
        from .tools import asset_loader
        asset_loader.show(root=os.path.expanduser("~"),
                          load=lambda name: None)
