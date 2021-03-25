"""Host API required Work Files tool"""
from .. import toonboom


def save_file(filepath):
    toonboom.save_file(filepath, "storyboardpro")
