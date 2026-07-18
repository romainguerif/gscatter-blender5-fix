from ...utils.logger import debug, info
from .effect_item import Effect
from ...common.store import AbstractNamespace
from pathlib import Path
from ...effects import default
from jsonschema.validators import validate
from jsonschema.exceptions import ValidationError
from . import schema
import json


class EffectNamespace(AbstractNamespace):
    def __init__(self, filepath: str, namespace: str) -> None:
        self._item_index: dict[str, Effect] = {}
        super().__init__(filepath, namespace)

    def add(self, item: Effect):
        if item.schema_version >= default.EFFECT_SCHEMA_VERSION:
            self._item_index[f"{item.id}:{item.version_str}"] = item
            item.namespace = self.namespace
            self.changes = True
            return item
        else:
            info(f"Effect schema version ({item.schema_version}) is outdated.")

    def add_from_filepath(self, filepath: str):
        f = open(filepath, "r")
        data: dict = json.load(f)
        f.close()

        if self.verify_effect(data):
            effect = Effect(
                data["id"],
                data["name"],
                data["author"],
                data["description"],
                data["icon"],
                data["categories"],
                data["subcategory"],
                data["effect_version"],
                data["schema_version"],
                data["blender_version"],
                data["node_group"],
            )
            effect.namespace = self.namespace
            blend_types = data.get("blend_types")
            if blend_types:
                effect.blend_types = blend_types
            default_blend_type = data.get("default_blend_type")
            if default_blend_type:
                effect.default_blend_type = default_blend_type
            return self.add(effect)

    def load(self, filepath: str):
        namespace_path = Path(filepath)

        if namespace_path.exists():
            f = open(self.filepath, "r")
            try:
                data = json.load(f)
            except Exception:
                f.close()
                self.store()
                return
            f.close()

            if self.verify_namespace(data):
                for effects in data["authors"].values():
                    effects = [list(effect.values()) for effect in effects.values()]
                    for effect in effects:
                        for version in effect:
                            for e in list(version.values()):
                                effect = Effect(
                                    e["id"],
                                    e["name"],
                                    e["author"],
                                    e["description"],
                                    e["icon"],
                                    e["categories"],
                                    e["subcategory"],
                                    e["effect_version"],
                                    e["schema_version"],
                                    e["blender_version"],
                                    e["node_group"],
                                )

                                effect.namespace = self.namespace
                                blend_types = e.get("blend_types")
                                if blend_types:
                                    effect.blend_types = blend_types
                                default_blend_type = e.get("default_blend_type")
                                if default_blend_type:
                                    effect.default_blend_type = default_blend_type
                                self._item_index.update(
                                    {f"{effect.id}:{effect.version_str}": effect}
                                )
            else:
                debug("Failed to verify store")

    def store(self):
        if self.changes:
            authors_dict = {}
            for effect in self._item_index.values():
                if not authors_dict.get(effect.author, None):
                    authors_dict.update({effect.author: {"effects": {}}})
                if authors_dict[effect.author]["effects"].get(effect.id) is None:
                    authors_dict[effect.author]["effects"].update({effect.id: {}})

                authors_dict[effect.author]["effects"][effect.id][
                    effect.version_str
                ] = effect.get_dict()

            data = {
                "schema_version": default.EFFECT_NAMESPACE_SCHEMA,
                "authors": authors_dict,
            }
            f = open(self.filepath, "w")
            json.dump(data, f, indent=4)
            f.close()
            self.changes = False

    def verify_namespace(self, data: dict) -> bool:
        schema_version = data.get("schema_version")
        if schema_version is None:
            return False

        if schema_version == default.EFFECT_NAMESPACE_SCHEMA:
            try:
                validate(instance=data, schema=schema.effect_namespace)
            except ValidationError:
                return False
            return True
        else:
            info("Old schema")
            return False

    def verify_effect(self, data: dict):
        try:
            schema_version = data["schema_version"]
        except KeyError:
            return False
        if schema_version == default.EFFECT_SCHEMA_VERSION:
            try:
                validate(instance=data, schema=schema.effect)
            except ValidationError:
                return False
            return True
        else:
            info("Old schema")
            return False
