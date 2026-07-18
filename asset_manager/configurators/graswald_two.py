from typing import TYPE_CHECKING

import bpy
from bpy.types import Collection
from ...utils.getters import get_preferences

from . import utils

if TYPE_CHECKING:
    from ..props.asset import AssetWidget

properties = {
    "Level Of Detail": {
        "items": ["0", "1", "2", "3", "4", "5", "6", "7"],
        "defaults": ["0", "1", "2", "3", "4", "5", "6", "7"],
    },
}


def configure(asset: "AssetWidget", lod=None, variant=None) -> Collection:
    """Use attributes and properties to import objects and assign materials."""
    prefs = get_preferences()
    if not variant:
        variant = utils.get_attribute(asset, "Variant")
    if not lod:
        level_of_detail = utils.get_property(asset, "Level Of Detail")
    else:
        level_of_detail = lod

    variant_lod = f"{variant}_lod{level_of_detail}"
    col_name = f"{asset.name} LOD{level_of_detail}:{asset.asset_id}"

    if col_name not in bpy.data.collections:
        collection = utils.new_collection(col_name)

        for blend in asset.blends.keys():
            with bpy.data.libraries.load(
                blend, link=prefs.asset_import_mode == "LINK", relative=True
            ) as (data_from, data_to):
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
