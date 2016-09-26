"""JSON Schema utilities

Schemas are implicitly loaded from the /schema directory of this project.

Attributes:
    _cache: Cache of previously loaded schemas

Resources:
    http://json-schema.org/
    http://json-schema.org/latest/json-schema-core.html
    http://spacetelescope.github.io/understanding-json-schema/index.html

"""

import os
import sys
import json
import logging

from .vendor import jsonschema

_log = logging.getLogger("pyblish-starter")

ValidationError = jsonschema.ValidationError


def validate(data, schema):
    """Validate `data` with `schema`

    Usage:
        >>> validate({"key": "value"}, "_doctest")
        >>> validate({"wrong": "value"}, "_doctest")
        Traceback (most recent call last):
        ...
        ValidationError: 'key' is a required property
        <BLANKLINE>
        Failed validating 'required' in schema:
            {'$schema': 'http://json-schema.org/schema#',
             'additionalProperties': False,
             'description': 'A test schema',
             'properties': {'key': {'description': 'A test key',
                                    'type': 'string'}},
             'required': ['key'],
             'title': '_doctest',
             'type': 'object'}
        <BLANKLINE>
        On instance:
            {'wrong': 'value'}

    Arguments:
        data (dict): JSON-compatible data
        schema (dict): jsonschema-compatible schema

    Raises:
        ValidationError on invalid schema

    """

    if isinstance(schema, basestring):
        schema = _cache[schema + ".json"]

    resolver = jsonschema.RefResolver(
        "",
        None,
        store=_cache,
        cache_remote=True
    )

    jsonschema.validate(data,
                        schema,
                        types={"array": (list, tuple)},
                        resolver=resolver)


if sys.version_info[0] == 3:
    basestring = str


_MODULE_DIR = os.path.dirname(__file__)
_SCHEMA_DIR = os.path.join(_MODULE_DIR, "schema")

_cache = {
    # A mock schema for docstring tests
    "_doctest.json": {
        "$schema": "http://json-schema.org/schema#",

        "title": "_doctest",
        "description": "A test schema",

        "type": "object",

        "additionalProperties": False,

        "required": ["key"],

        "properties": {
            "key": {
                "description": "A test key",
                "type": "string"
            }
        }
    }
}


def _precache():
    """Store available schemas in-memory for reduced disk access"""
    for schema in os.listdir(_SCHEMA_DIR):
        if schema.startswith(("_", ".")):
            continue
        if not schema.endswith(".json"):
            continue
        if not os.path.isfile(os.path.join(_SCHEMA_DIR, schema)):
            continue
        with open(os.path.join(_SCHEMA_DIR, schema)) as f:
            _log.debug("Installing schema '%s'.." % schema)
            _cache[schema] = json.load(f)


_precache()
