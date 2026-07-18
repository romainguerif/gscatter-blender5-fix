from typing import TYPE_CHECKING

import bpy
from ...utils.getters import get_preferences

from . import utils

if TYPE_CHECKING:
    from ..props.asset import AssetWidget

properties = {}


def configure(asset: "AssetWidget") -> bpy.types.Collection:
    """Import all objects from the asset."""
    prefs = get_preferences()
    col_name = f"{asset.name}:{asset.asset_id}"
    if col_name not in bpy.data.collections:
        collection = utils.new_collection(col_name)

        for blend in asset.blends.keys():
            with bpy.data.libraries.load(
                blend, link=prefs.asset_import_mode == "LINK", relative=True
            ) as (data_from, data_to):
                data_to.objects = data_from.objects

            for obj in data_to.objects:
                collection.objects.link(obj)

                utils.apply_shape_keys(obj)
                utils.apply_transforms(obj)
    else:
        collection = bpy.data.collections[col_name]
    return collection
