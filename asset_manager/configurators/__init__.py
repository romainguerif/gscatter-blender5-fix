from typing import TYPE_CHECKING

import bpy

from . import graswald_one, graswald_two, graswald_three, standard

if TYPE_CHECKING:
    from ..props.asset import AssetWidget

modules = {
    "standard": standard,
    "graswald_one": graswald_one,
    "graswald_two": graswald_two,
    "graswald_three": graswald_three,
}


def configure(asset: "AssetWidget", lod=None, variant=None) -> bpy.types.Collection:
    """Configure and import the asset."""
    module = modules.get(asset.configurator.name, standard)
    return module.configure(asset, lod, variant)
