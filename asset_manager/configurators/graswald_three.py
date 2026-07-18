from typing import TYPE_CHECKING

import bpy
from bpy.types import Collection

from . import utils

if TYPE_CHECKING:
    from ..props.asset import AssetWidget

properties = {
    "Level Of Detail": {
        "items": ["0", "1", "2", "3", "4", "5", "6", "7"],
        "defaults": ["0", "1", "2", "3", "4", "5", "6", "7"],
    },
    "Texture Resolution": {
        "items": ["1k", "2k", "4k", "8k"],
        "defaults": ["1k", "2k", "4k", "8k"],
    },
}


def configure(asset: "AssetWidget") -> Collection:
    """Use attributes and properties to import objects and assign materials."""
    variant = utils.get_attribute(asset, "Variant")
    level_of_detail = utils.get_property(asset, "Level Of Detail")

    variant_lod = f"{variant}_lod{level_of_detail}"
    col_name = f"{asset.name} LOD{level_of_detail}:{asset.asset_id}"
    if col_name not in bpy.data.collections:
        collection = utils.new_collection(col_name)

        for blend in asset.blends.keys():
            with bpy.data.libraries.load(blend) as (data_from, data_to):
                data_to.collections.append(variant_lod)

            for col in data_to.collections:
                objects = list(col.objects)
                bpy.data.collections.remove(col)

                for object in objects:
                    collection.objects.link(object)
                    utils.apply_transforms(object)
    else:
        collection = bpy.data.collections.get(col_name)

    return collection
