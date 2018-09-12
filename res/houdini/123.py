"""
DO NOT RENAME THIS MODULE!:
http://www.sidefx.com/docs/houdini/hom/locations.html

Run whenever Houdini is started without a scene file
"""
from avalon import pipeline, houdini


print("Installing Avalon ...")
pipeline.install(houdini)
