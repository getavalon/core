# Test io.delete_many
import contextlib
import os
import re
import json

from nose.tools import with_setup
import pymongo

import avalon.io
import avalon.inventory


project_name = "batman"

datetime_regex = (
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}\+"
    "[0-9]{2}:[0-9]{2}"
)

os.environ["AVALON_PROJECT"] = project_name
os.environ["AVALON_ASSET"] = "bruce"
os.environ["AVALON_SILO"] = "assets"
avalon.io.install()


@contextlib.contextmanager
def setup():
    avalon.io.delete_many({})


@with_setup(setup)
def test_insert_one():
    """Insert one works with events."""

    avalon.io.insert_one(
        {
            "schema": "avalon-core:project-2.0",
            "type": "project",
            "name": project_name,
            "data": dict(),
            "config": {
                "schema": "avalon-core:config-1.0",
                "apps": [],
                "tasks": [],
                "template": {"publish": ""}
            },
            "parent": None,
        }
    )

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    events = db[project_name].find({"type": "event"})

    # Should only be one event at this point.
    assert events.count() == 1

    assert events[0]["method"] == "insert_one"

    assert len(json.loads(events[0]["args"])) == 1
    assert len(events[0]["kwargs"]) == 0

    assert re.compile(datetime_regex).match(events[0]["datetime"]) is not None


@with_setup(setup)
def test_insert_many():
    """Insert many works with events."""

    avalon.io.insert_many(
        [
            {
                "schema": "avalon-core:asset-2.0",
                "name": "bruce",
                "silo": "characters",
                "parent": None,
                "type": "asset",
                "data": {}
            }
        ]
    )

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    events = db[project_name].find({"type": "event"})

    # Should only be one event at this point.
    assert events.count() == 1

    assert events[0]["method"] == "insert_many"

    assert len(json.loads(events[0]["args"])) == 1
    assert len(events[0]["kwargs"]) == 1

    assert re.compile(datetime_regex).match(events[0]["datetime"]) is not None


@with_setup(setup)
def test_replace_one():
    """Replace one works with events."""

    avalon.io.insert_one(
        {
            "schema": "avalon-core:asset-2.0",
            "name": "bruce",
            "silo": "characters",
            "parent": None,
            "type": "asset",
            "data": {}
        }
    )

    avalon.io.replace_one(
        {"type": "asset", "name": "bruce"},
        {
            "schema": "avalon-core:asset-2.0",
            "name": "joker",
            "silo": "characters",
            "parent": None,
            "type": "asset",
            "data": {}
        }
    )

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]

    events = db[project_name].find({"type": "event"})
    assert events.count() == 2

    event = db[project_name].find_one(
        {"type": "event", "method": "replace_one"}
    )
    assert event is not None

    assert len(json.loads(event["args"])) == 2
    assert len(event["kwargs"]) == 0

    regex_match = re.compile(datetime_regex).match(event["datetime"])
    assert regex_match is not None


@with_setup(setup)
def test_update_many():
    """Update many works with events."""

    avalon.io.insert_many(
        [
            {
                "schema": "avalon-core:asset-2.0",
                "name": "bruce",
                "silo": "characters",
                "parent": None,
                "type": "asset",
                "data": {}
            },
            {
                "schema": "avalon-core:asset-2.0",
                "name": "joker",
                "silo": "characters",
                "parent": None,
                "type": "asset",
                "data": {}
            }
        ]
    )

    avalon.io.update_many({"silo": "characters"}, {"$set": {"silo": "assets"}})

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]

    events = db[project_name].find({"type": "event"})
    assert events.count() == 2

    event = db[project_name].find_one(
        {"type": "event", "method": "update_many"}
    )
    assert event is not None

    assert len(json.loads(event["args"])) == 2
    assert len(event["kwargs"]) == 0

    regex_match = re.compile(datetime_regex).match(event["datetime"])
    assert regex_match is not None


@with_setup(setup)
def test_delete_many():
    """Delete many works with events."""

    avalon.io.insert_many(
        [
            {
                "schema": "avalon-core:asset-2.0",
                "name": "bruce",
                "silo": "characters",
                "parent": None,
                "type": "asset",
                "data": {}
            },
            {
                "schema": "avalon-core:asset-2.0",
                "name": "joker",
                "silo": "characters",
                "parent": None,
                "type": "asset",
                "data": {}
            }
        ]
    )

    avalon.io.delete_many({"silo": "characters"})

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]

    events = db[project_name].find({"type": "event"})
    assert events.count() == 2

    event = db[project_name].find_one(
        {"type": "event", "method": "delete_many"}
    )
    assert event is not None

    assert len(json.loads(event["args"])) == 1
    assert len(event["kwargs"]) == 0

    regex_match = re.compile(datetime_regex).match(event["datetime"])
    assert regex_match is not None
