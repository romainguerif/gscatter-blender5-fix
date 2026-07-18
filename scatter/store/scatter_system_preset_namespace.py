from ...utils.logger import debug, info
from .scatter_system_preset_item import ScatterSystemPreset
from ...common.store import AbstractNamespace
from ...effects import default
from jsonschema.validators import validate
from jsonschema.exceptions import ValidationError
from . import schema
from pathlib import Path
import json


class ScatterSystemPresetNamespace(AbstractNamespace):
    def __init__(self, filepath: str, namespace: str) -> None:
        self._item_index: dict[str, ScatterSystemPreset] = {}
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
                    distribution = preset_data["distribution"]
                    scale = preset_data["scale"]
                    rotation = preset_data["rotation"]
                    geometry = preset_data["geometry"]
                    preset = ScatterSystemPreset(
                        preset_data["id"],
                        preset_data["name"],
                        preset_data.get("is_terrain", False),
                        distribution,
                        scale,
                        rotation,
                        geometry,
                    )
                    preset.namespace = self.namespace
                    self._item_index[preset.id] = preset
            else:
                info("Verification failed: Scatter System Preset")

    def store(self):
        if self.changes:
            data = {
                "schema_version": default.SCATTER_SYSTEM_PRESET_NAMESPACE_SCHEMA,
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

        if schema_version == default.SCATTER_SYSTEM_PRESET_NAMESPACE_SCHEMA:
            try:
                validate(instance=data, schema=schema.scatter_system_preset)
            except ValidationError:
                return False
            return True
        else:
            debug("Old schema")
            return False
