from typing import Union
from pathlib import Path
from copy import copy
import bpy

from ...utils.logger import info
from .effect_item import Effect
from .effect_namespace import EffectNamespace
from ...common.store import AbstractStore
from ...utils.getters import get_preferences


class EffectStore(AbstractStore):
    namespace: dict[str, EffectNamespace] = {}
    _item_index: dict[str, Effect] = {}

    def __init__(self) -> None:
        super().__init__()
        presets_dir = Path(__file__).parent
        self.load(presets_dir.joinpath("effect_store.json"), "system")
        self.load(presets_dir.joinpath("internal_effect_store.json"), "internal")

    def add(self, namespace: str, effect: Effect):
        effect_namespace = self.namespace.get(namespace)
        if effect_namespace:
            added_effect = effect_namespace.add(effect)
            if added_effect:
                self._item_index[f"{added_effect.id}:{added_effect.version_str}"] = (
                    added_effect
                )
        else:
            info(f"Could not add effect. {effect.name}")

    def add_from_filepath(self, filepath: str):
        namespace = self.namespace.get("user")
        effect = namespace.add_from_filepath(filepath)
        if effect:
            self._item_index.update({f"{effect.id}:{effect.version_str}": effect})
        else:
            info("Could not add effect from filepath.")

    def remove(self, item: Effect):
        effect = self._item_index.get(f"{item.id}:{item.version_str}")
        if effect:
            del self._item_index[f"{effect.id}:{effect.version_str}"]
            effect_namespace = self.namespace.get(effect.namespace)
            effect_namespace.remove(f"{item.id}:{item.version_str}")

    def get_by_id(self, item_id: str) -> list[Effect]:
        effects = [
            copy(effect)
            for effect in self._item_index.values()
            if effect.id == item_id and effect.blender_version <= list(bpy.app.version)
        ]
        return effects

    def get_newest_by_id(self, item_id: str) -> Union[Effect, None]:
        effects = [
            effect
            for effect in self._item_index.values()
            if effect.id == item_id and effect.blender_version <= list(bpy.app.version)
        ]
        if len(effects) > 0:
            effects.sort(key=lambda effect: effect.effect_version, reverse=True)
            return copy(effects[0])
        return None

    def get_by_id_and_version(self, item_id: str, version: list[int]) -> Effect:
        effects = [
            copy(effect)
            for effect in self._item_index.values()
            if effect.id == item_id and effect.effect_version == version
        ]
        if len(effects) > 0:
            return effects[0]

    def get_newest_by_name(self, author: str, name: str) -> Effect:
        """Get the newest version of an effect by name and author"""
        effects = [
            effect
            for effect in self._item_index.values()
            if effect.name == name
            and effect.author == author
            and effect.blender_version <= list(bpy.app.version)
        ]
        effects.sort(key=lambda effect: effect.effect_version, reverse=True)
        return copy(effects[0])

    def get_all(self) -> list[Effect]:
        return super().get_all()

    def update(self, effect_version: list[int], item: Effect):
        """Update an effect

        Parameters
        ----------
        effect_version: list[int]
            the original version of the effect

        item: Effect
            the effect with updated properties
        """
        original = [
            effect
            for effect in self._item_index.values()
            if effect.id == item.id and effect.effect_version == effect_version
        ][0]
        if original:
            if item.effect_version == original.effect_version:
                del self._item_index[f"{item.id}:{original.version_str}"]
                original.name = item.name
                original.author = item.author
                original.description = item.description
                original.icon = item.icon
                original.categories = item.categories
                original.subcategory = item.subcategory
                original.effect_version = item.effect_version
                original.schema_version = item.schema_version
                original.blender_version = item.blender_version
                original.blend_types = item.blend_types
                original.default_blend_type = item.default_blend_type
                original._nodetree = item._nodetree
                # self._item_index[f"{item.id}:{original.version_str}"] = original
                self.add(original.namespace, original)
            else:
                self.add(item.namespace, item)

    def load(self, filepath: str, namespace: str):
        effect_namespace = EffectNamespace(filepath, namespace)
        self.namespace[namespace] = effect_namespace
        for effect in effect_namespace._item_index.values():
            self._item_index[f"{effect.id}:{effect.version_str}"] = effect

    def merge(self, filepath: str, namespace: str):
        effect_namespace = EffectNamespace(filepath, namespace)

        has_namespace = self.namespace.get(namespace)
        if has_namespace:
            for effect in effect_namespace._item_index.values():
                has_namespace.add(effect)
        else:
            self.namespace[namespace] = effect_namespace
        for effect in effect_namespace._item_index.values():
            self._item_index[f"{effect.id}:{effect.version_str}"] = effect

    def _load_user_namespace(self):
        prefs = get_preferences(bpy.context)
        store_path = Path(prefs.t3dn_library, "effect_store.json").as_posix()
        self.load(store_path, "user")
