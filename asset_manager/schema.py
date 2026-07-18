from jsonschema.validators import validate
from jsonschema.exceptions import ValidationError

environment_json = {
    "type": "object",
    "properties": {
        "asset_type": {"type": "string"},
        "asset_id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "author": {"type": "string"},
        "schema_version": {"type": "array"},
        "gscatter_systems": {"type": "array"},
        "blends": {"type": "array"},
        "preview": {"type": "string"},
        "gscatter_assets": {"type": "array"},
        "environment_props": {"type": "array"},
        "terrain": {"type": "object"},
    },
}

asset_json = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "authors": {"type": "object"},
        "assets": {"type": "array"},
    },
}


def verify_asset(data: dict):
    try:
        validate(instance=data, schema=asset_json)
    except ValidationError:
        return False
    return True


def verify_environment(data: dict):
    try:
        validate(instance=data, schema=environment_json)
    except ValidationError:
        return False
    return True
