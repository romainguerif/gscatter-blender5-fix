import json

import bpy

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from .. import default
from . import schema
from .effect_item import Effect


class EffectDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):  # -> Effect | Any:
        if self.verify_effect(obj):
            return Effect(
                obj["id"],
                obj["name"],
                obj["author"],
                obj["description"],
                obj["icon"],
                obj["categories"],
                obj["subcategory"],
                obj["effect_version"],
                obj["schema_version"],
                obj["blender_version"],
                obj["node_group"],
            )
        return obj

    def verify_effect(self, data: dict):
        try:
            schema_version = data["schema_version"]
        except KeyError:
            return False
        if schema_version <= default.EFFECT_SCHEMA_VERSION and data[
            "blender_version"
        ] >= list(bpy.app.version):
            try:
                validate(instance=data, schema=schema.effect)
            except ValidationError:
                return False
            return True
        else:
            print("GScatter: Old Effect Schema")
            return False
