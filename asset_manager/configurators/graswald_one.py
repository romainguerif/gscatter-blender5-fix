from typing import TYPE_CHECKING, List

import bpy
from bpy.types import Collection

from ...utils.getters import get_preferences
from . import utils

if TYPE_CHECKING:
    from ..props.asset import AssetWidget

properties = {
    "Grow Type": {
        "items": ["Single", "Clump"],
        "defaults": ["Clump", "Single"],
    },
    "Level Of Detail": {
        "items": ["Proxy", "Low", "High"],
        "defaults": ["High", "Low", "Proxy"],
    },
    "Material Quality": {
        "items": ["Low", "Medium", "High"],
        "defaults": ["High", "Medium", "Low"],
    },
}


def find_material(materials: List[str], words: List[str]) -> str:
    """Find the material with the most of the given words in its name."""
    highest = -1
    best = None

    for material in materials:
        count = sum(1 for word in words if word in material)

        if count > highest:
            highest = count
            best = material

    return best


def configure(asset: "AssetWidget", lod=None, variant=None) -> Collection:
    """Use attributes and properties to import objects and assign materials."""
    prefs = get_preferences()
    life_cycle = utils.get_attribute(asset, "Life Cycle")
    height_key = utils.get_attribute(asset, "Height Key")
    grow_type = utils.get_property(asset, "Grow Type")
    level_of_detail = utils.get_property(asset, "Level Of Detail")
    material_quality = utils.get_property(asset, "Material Quality")

    prefs = get_preferences()
    if not variant:
        variant = utils.get_attribute(asset, "Variant")
    if not lod:
        level_of_detail = utils.get_property(asset, "Level Of Detail")
    else:
        level_of_detail = lod

    col_name = f"{asset.name} LOD{level_of_detail}:{asset.asset_id}"

    col_name = " ".join((asset.name, grow_type, level_of_detail))
    col_name += f":{asset.asset_id}"
    if col_name not in bpy.data.collections:
        collection = utils.new_collection(col_name)
        material_words = asset.name.split() + [material_quality]
        if life_cycle in material_words:
            material_words.remove(life_cycle)

        life_cycle = "_" + life_cycle
        height_key = float(height_key) if height_key else None
        grow_type = grow_type.upper()
        level_of_detail = level_of_detail.upper()

        for blend in asset.blends.keys():
            with bpy.data.libraries.load(
                blend, link=prefs.asset_import_mode == "LINK", relative=True
            ) as (data_from, data_to):
                for obj_name in data_from.objects:
                    if all(
                        text in obj_name
                        for text in (life_cycle, grow_type, level_of_detail)
                    ):
                        data_to.objects.append(obj_name)

                if material_quality:
                    best_material = find_material(data_from.materials, material_words)
                    data_to.materials.append(best_material)

            for obj in data_to.objects:
                collection.objects.link(obj)

                if height_key is not None:
                    utils.set_height_shape(obj, height_key)

                utils.apply_shape_keys(obj)
                utils.apply_transforms(obj)

            if material_quality:
                for mat in data_to.materials:
                    if best_material in mat.name:
                        for obj in data_to.objects:
                            obj.data.materials.clear()
                            obj.data.materials.append(mat)
                    else:
                        bpy.data.materials.remove(mat)
    else:
        collection = bpy.data.collections[col_name]
    return collection
