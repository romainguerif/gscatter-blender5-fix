from pathlib import Path
from copy import copy
import bpy
from .effect_preset import EffectPreset
from .effect_preset_namespace import EffectPresetNamespace
from ...common.store import AbstractStore
from ...utils.getters import get_preferences


class EffectPresetStore(AbstractStore):
    namespace: dict[str, EffectPresetNamespace] = {}
    _item_index: dict[str, EffectPreset] = {}

    def __init__(self) -> None:
        super().__init__()
        presets_dir = Path(__file__).parent
        self.load(presets_dir.joinpath("effect_preset_store.json"), "system")

    def get_by_id(self, item_id: str) -> EffectPreset:
        return super().get_by_id(item_id)

    def get_by_effect_id(self, effect_id: str) -> list[EffectPreset]:
        presets = [
            copy(preset)
            for preset in self._item_index.values()
            if preset.effect_id == effect_id
        ]
        return presets

    def get_by_effect_id_and_version(
        self, effect_id: str, effect_version: list[int]
    ) -> list[EffectPreset]:
        presets = [
            copy(preset)
            for preset in self._item_index.values()
            if preset.effect_id == effect_id and preset.effect_version == effect_version
        ]
        return presets

    def update(self, item: EffectPreset):
        original_preset = self._item_index.get(item.id)
        if original_preset:
            original_preset.name = item.name
            original_preset.effect_id = item.effect_id
            original_preset.params = item.params
            original_preset.layer_params = item.layer_params

    def load(self, filepath: str, namespace: str):
        preset_namespace = EffectPresetNamespace(filepath, namespace)
        self.namespace[namespace] = preset_namespace
        for preset in preset_namespace._item_index.values():
            self._item_index[preset.id] = preset

    def merge(self, filepath: str, namespace: str):
        preset_namespace = EffectPresetNamespace(filepath, namespace)

        has_namespace = self.namespace.get(namespace)
        if has_namespace:
            for preset in preset_namespace._item_index.values():
                has_namespace.add(preset)
        else:
            self.namespace[namespace] = preset_namespace
        for preset in preset_namespace._item_index.values():
            self._item_index[preset.id] = preset

    def _load_user_namespace(self):
        prefs = get_preferences(bpy.context)
        store_path = Path(prefs.t3dn_library, "effect_preset_store.json").as_posix()
        self.load(store_path, "user")
