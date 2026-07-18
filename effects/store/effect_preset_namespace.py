from pathlib import Path
import json

from ...utils.logger import info
from .effect_preset import EffectPreset
from ...common.store import AbstractNamespace
from .. import default
from jsonschema.validators import validate
from jsonschema.exceptions import ValidationError
from . import schema


class EffectPresetNamespace(AbstractNamespace):
    def __init__(self, filepath: str, namespace: str) -> None:
        self._item_index: dict[str, EffectPreset] = {}
        super().__init__(filepath, namespace)

    def load(self, filepath: str):
        namespace_path = Path(filepath)
        if namespace_path.exists():
            file = open(filepath, "r")
            try:
                data = json.load(file)
            except Exception:
                file.close()
                self.store()
                return
            file.close()

            if self.verify_namespace(data):
                for preset_data in data["presets"].values():
                    preset = EffectPreset(
                        preset_data["id"],
                        preset_data["name"],
                        preset_data["effect_id"],
                        preset_data["effect_version"],
                        preset_data["params"],
                        preset_data["layer_params"],
                        preset_data["nodes"],
                        preset_data.get("dropdowns", {}),
                    )

                    preset.namespace = self.namespace
                    self._item_index[preset.id] = preset

    def store(self):
        if self.changes:
            data = {
                "schema_version": default.EFFECT_PRESET_NAMESPACE_SCHEMA,
                "presets": {},
            }

            for preset in self._item_index:
                data["presets"][preset] = self._item_index[preset].get_dict()

            file = open(self.filepath, "w")
            json.dump(data, file, indent=4)
            file.close()
            self.changes = False

    def verify_namespace(self, data: dict) -> bool:
        schema_version = data.get("schema_version")
        if schema_version is None:
            return False

        if schema_version == default.EFFECT_PRESET_NAMESPACE_SCHEMA:
            try:
                validate(instance=data, schema=schema.effect_preset_namespace)
            except ValidationError:
                return False
            return True
        else:
            info("Old schema")
            return False
