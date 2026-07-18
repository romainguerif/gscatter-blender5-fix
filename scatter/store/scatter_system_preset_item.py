from ...common.store import AbstractStoreItem
from ...effects import default


class ScatterSystemPreset(AbstractStoreItem):
    def __init__(
        self,
        id: str,
        name: str,
        is_terrain: bool,
        distribution: list[dict],
        scale: list[dict],
        rotation: list[dict],
        geometry: list[dict],
    ) -> None:
        super().__init__(id)
        self.name = name
        self.distribution = distribution
        self.is_terrain = is_terrain
        self.scale = scale
        self.rotation = rotation
        self.geometry = geometry

    def get_dict(self) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "is_terrain": self.is_terrain,
            "schema_version": default.SCATTER_SYSTEM_PRESET_SCHEMA,
            "distribution": self.distribution,
            "scale": self.scale,
            "rotation": self.rotation,
            "geometry": self.geometry,
        }
        return data
