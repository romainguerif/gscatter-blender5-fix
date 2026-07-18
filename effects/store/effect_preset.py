from ...common.store import AbstractStoreItem
from ...effects import default


class EffectPreset(AbstractStoreItem):
    def __init__(
        self,
        id: str,
        name: str,
        effect_id: str,
        effect_version: list[int],
        params: dict,
        layer_params: dict,
        nodes: dict,
        dropdowns: dict,
    ) -> None:
        super().__init__(id)
        self.name = name
        self.effect_id = effect_id
        self.effect_version = effect_version
        self.params = params
        self.layer_params = layer_params
        self.nodes = nodes
        self.dropdowns = dropdowns

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "effect_id": self.effect_id,
            "effect_version": self.effect_version,
            "params": self.params,
            "layer_params": self.layer_params,
            "nodes": self.nodes,
            "dropdowns": self.dropdowns,
            "schema_version": default.EFFECT_PRESET_SCHEMA,
        }
