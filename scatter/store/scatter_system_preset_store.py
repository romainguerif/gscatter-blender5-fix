from .scatter_system_preset_namespace import ScatterSystemPresetNamespace
from .scatter_system_preset_item import ScatterSystemPreset
from ...common.store import AbstractStore
from ...utils.getters import get_preferences
from pathlib import Path
import bpy


class ScatterSystemPresetStore(AbstractStore):
    namespace: dict[str, ScatterSystemPresetNamespace] = {}
    _item_index: dict[str, ScatterSystemPreset] = {}

    def __init__(self) -> None:
        super().__init__()
        presets_dir = Path(__file__).parent
        self.load(presets_dir.joinpath("scatter_system_preset_store.json"), "system")

    def update(self, item: ScatterSystemPreset):
        original_preset = self._item_index.get(item.id)
        if original_preset:
            original_preset.name = item.name
            original_preset.distribution = item.distribution
            original_preset.scale = item.scale
            original_preset.rotation = item.rotation
            original_preset.geometry = item.geometry

    def load(self, filepath: str, namespace: str):
        preset_namespace = ScatterSystemPresetNamespace(filepath, namespace)
        self.namespace[namespace] = preset_namespace
        for preset in preset_namespace._item_index.values():
            self._item_index[preset.id] = preset

    def merge(self, filepath: str, namespace: str):
        preset_namespace = ScatterSystemPresetNamespace(filepath, namespace)

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
        store_path = Path(prefs.t3dn_library, "system_preset_store.json").as_posix()
        self.load(store_path, "user")

    def get_by_id(self, item_id: str) -> ScatterSystemPreset:
        return super().get_by_id(item_id)
