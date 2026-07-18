# This is duplicated code from asset_manager.utils and asset_manager.configurators.utils
# It should be removed in favour of a better structure
# For the moment we keep it to avoid cyclic dependencies and refactoring

import blf
import bpy

from . import startup
from .getters import get_preferences

modules = (startup,)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()


def main_collection(name: str = None, sub: str = None) -> bpy.types.Collection:
    """Get the main collection from the active scene. Optionally get a subcollection of the main collection."""
    scene = bpy.context.scene
    prefs = get_preferences()

    if name is None:
        name = prefs.gscatter_collection_name

    for collection in scene.collection.children.values():
        if collection.name.startswith(name):
            break
    else:
        if name not in bpy.data.collections:
            collection = bpy.data.collections.new(name)
        collection = bpy.data.collections[name]
        scene.collection.children.link(collection)

    if sub is not None:
        for subcollection in collection.children.values():
            if subcollection.name.startswith(sub):
                break
        else:
            if sub not in bpy.data.collections:
                subcollection = bpy.data.collections.new(sub)
            subcollection = bpy.data.collections[sub]
            collection.children.link(subcollection)
            # Exclude collection in viewlayers
            if sub.startswith("Sources"):
                view_layer: bpy.types.ViewLayer
                for view_layer in bpy.context.scene.view_layers:
                    view_layer.layer_collection.children[collection.name].children[
                        subcollection.name
                    ].exclude = True
                    subcollection.hide_render = True
        return subcollection

    return collection


def new_collection(name: str) -> bpy.types.Collection:
    """Create a collection in the main collection."""
    parent = main_collection(sub="Assets")

    child = bpy.data.collections.new(name)
    parent.children.link(child)

    return child


def recursive_exclude(
    layer_collection: bpy.types.LayerCollection, coll: bpy.types.Collection
) -> None:
    if layer_collection.collection == coll:
        layer_collection.exclude = True
        return
    for lc in layer_collection.children:
        recursive_exclude(lc, coll)


def wrap_text(text: str, width: int) -> list[str]:
    """
    Wrap the given text to the given width.

    Args:
        width: The maximum pixel width of each row.
        text: The text to be split and returned.

    Returns:
        A list of the split up text and empty space if necessary.
    """
    return_text = []
    row_text = ""

    system = bpy.context.preferences.system
    # dpi = 72 if system.ui_scale >= 1 else system.dpi
    blf.size(0, 11)

    for word in text.split():
        word = f" {word}"
        line_len, _ = blf.dimensions(0, row_text + word)
        max_width = ((width) / (system.ui_scale)) - 100

        if line_len <= max_width:
            row_text += word
        else:
            return_text.append(row_text)
            row_text = word

    if row_text:
        return_text.append(row_text)

    return return_text
