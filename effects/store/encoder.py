import json
from .effect_item import Effect


class EffectEncoder(json.JSONEncoder):
    def default(self, obj) -> str:
        if isinstance(obj, Effect):
            obj: Effect
            data = {
                "id": obj.id,
                "name": obj.name,
                "author": obj.author,
                "description": obj.description,
                "icon": obj.icon,
                "categories": obj.categories,
                "subcategory": obj.subcategory,
                "effect_version": list(obj.effect_version),
                "schema_version": list(obj.schema_version),
                "blender_version": list(obj.blender_version),
                "node_group": obj._nodetree,
            }
            return data
        return json.JSONEncoder.default(self, obj)
