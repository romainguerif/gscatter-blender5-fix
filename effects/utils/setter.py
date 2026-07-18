import random
from typing import TYPE_CHECKING

import bpy

from ...utils import recursive_exclude

from ...utils.logger import debug, error

from ...asset_manager.configurators import configure
from ...utils.getters import get_nodes_from_node_tree
from .. import utils
from ..store import effectstore
from ..utils import main_collection

if TYPE_CHECKING:
    from ...asset_manager.props.library import LibraryWidget


def set_colorramp_points(node, color_ramp):
    index = 0
    for el in node.color_ramp.elements:
        if len(node.color_ramp.elements) > 1:
            try:
                node.color_ramp.elements.remove(node.color_ramp.elements[index])
            except Exception:
                index += 1

    node.color_ramp.elements[0].position = 0.0

    i = 0
    for pos, color in color_ramp[:1]:
        c = node.color_ramp.elements[i]
        c.position = pos
        c.color = color
        i += 1
    for pos, color in color_ramp[1:]:
        c = node.color_ramp.elements.new(pos)
        c.color = color


def set_curve_float_points(node, curve_float):
    index = 0
    for curve_idx, curve in enumerate(node.mapping.curves):
        for point in curve.points:
            if len(curve.points) > index:
                try:
                    curve.points.remove(curve.points[index])
                except Exception:
                    index += 1
        curve.points[0].location = (0, 0)
        curve.points[1].location = (1, 1)
        node.mapping.update()

        for i, p in enumerate(curve_float[curve_idx][1:-1]):
            i += 1
            curve.points.new(p[0][0], p[0][1])
            curve.points[i].handle_type = p[1]
        point_first = curve_float[curve_idx][0]
        point_last = curve_float[curve_idx][-1]
        curve.points[0].handle_type = point_first[1]
        curve.points[0].location = point_first[0]
        curve.points[-1].handle_type = point_last[1]
        curve.points[-1].location = point_last[0]
        node.mapping.update()


def set_effect_properties(
    effect_datas: list[dict],
    ntree: bpy.types.GeometryNodeTree,
    main_node: str,
    effect_trees: dict,
    skip_params_check: bool = False,
    collection: bpy.types.Collection = None,
    new_instance: bool = False,
):
    # scene_props = get_scene_props(bpy.context)
    effects_missing = None
    for effect_data in effect_datas:
        effect_name = effect_data.get("name")
        effect_id = effect_data["effect_id"]
        effect_version = effect_data["effect_version"]

        effect_available = effectstore.get_newest_by_id(effect_id)
        if effect_available is None:
            effects_missing = True if effects_missing is None else None
            continue
        effect_version = effect_available.effect_version

        effect_ntree = None
        new = True
        if effect_name and effect_name in effect_trees:
            effect_ntree = effect_trees[effect_name]
            new = False

        if new:
            effect_ntree = effect_available.nodetree
            effect_ntree.name = effect_name

        # if effect_available.schema_version < EFFECT_SCHEMA_VERSION:
        #     continue

        effect = utils.add_effect(
            effect_ntree,
            ntree,
            main_node,
            effect_id,
            effect_version,
            effect_data.get("effect_instance_id") if not new_instance else None,
            new,
        )

        if new and effect_name:
            effect_trees[effect_name] = effect.group_node.node_tree

        try:
            if effect_id == "system.instance_collection" and collection:
                effect.effect_node.inputs["Collection"].default_value = collection

            elif effect_id == "system.distribute_on_faces":
                effect.effect_node.inputs["Seed"].default_value = random.randint(0, 100)
        except Exception as e:
            error(
                "Failed to set effect default value for %s %e" % effect.name % e,
                debug=True,
            )
            pass

        if skip_params_check:
            continue

        if effect_data.get("dropdowns"):
            set_dropdown(effect, effect_data.get("dropdowns"))

        if effect_data["params"]:
            set_params(effect.effect_node, effect_data["params"], collection)

        if effect_data["layer_params"]:
            set_layer_params(effect, effect_data["layer_params"])

        if effect_data["nodes"]:
            set_node_props(effect, effect_data["nodes"], effect_id)

    return effects_missing


def set_dropdown(effect, dropdowns):
    # Clear dropdown items and assign new
    effect.add_dropdown_items()
    if dropdowns:
        for dropdown_key in dropdowns.keys():
            value = dropdowns[dropdown_key]
            for dropdown in effect.dropdowns:
                if dropdown.name == dropdown_key:
                    try:
                        dropdown.dropdown_items = value
                    except Exception as e:
                        try:
                            dropdown.dropdown_items = value.replace("Output", "Socket")
                        except Exception as e:
                            debug(f"Failed to update {dropdown_key} to {value}\n {e}")
                        debug(f"Failed to update {dropdown_key} to {value} \n {e}")
                    break


def set_node_props(effect, node_props, effect_id):
    nodes = set()
    get_nodes_from_node_tree(effect.effect_node.node_tree, nodes)
    for node_name in node_props.keys():
        try:
            node = next(node for node in nodes if node.name == node_name)
        except Exception as e:
            debug(f"Failed to find node {node_name} \n {e}")
            continue

        props = node_props[node_name]

        for prop in props["props"]:
            setattr(node, prop, props["props"][prop])

        if "color_ramp" in props:
            set_colorramp_points(node, props["color_ramp"])
            if "color_ramp_props" in props:
                ramp_props = props["color_ramp_props"]
                node.color_ramp.color_mode = ramp_props["color_mode"]
                node.color_ramp.interpolation = ramp_props["interpolation"]
                node.color_ramp.hue_interpolation = ramp_props["hue_interpolation"]

        elif "curve_float" in props:
            set_curve_float_points(node, props["curve_float"])
        elif "curve_rgb" in props:
            set_curve_float_points(node, props["curve_rgb"])

        if "params" in props:
            set_params(node, props["params"])


def set_layer_params(effect, layer_params):
    if effect.mix_node:
        if layer_params["blendmode"] in effect.blend_types:
            effect.blend_type = layer_params["blendmode"]
        influence = int(layer_params["influence"]) * 100
        effect.influence = influence if influence <= 100 else int(influence / 100)
        if "invert" in layer_params:
            effect.invert = layer_params["invert"]


def set_params(node, params, collection=None):
    for input in params:
        # debug(params[input])
        if isinstance(params[input], dict):
            if params[input]["type"] == "OBJECT" and params[input]["name"]:
                ob = bpy.data.objects.get(params[input]["name"])
                if ob:
                    node.inputs["Object"].default_value = ob
            elif params[input]["type"] == "COLLECTION":
                library: "LibraryWidget" = bpy.context.window_manager.gscatter.library
                col_prop = params[input]
                if col_prop.get("is_gscatter_asset") and collection is None:
                    asset_id = col_prop["asset_id"]
                    variant = col_prop["variant"]
                    lod = col_prop["lod"]
                    asset = [
                        ass
                        for ass in library.assets
                        if ass.asset_id == asset_id and variant in ass.name
                    ]

                    if asset:
                        asset = asset[0]
                        collection = configure(asset, lod, variant)
                        collection.gscatter.is_gscatter_asset = True
                        collection.gscatter.asset_id = asset_id

                        col_sources = main_collection(sub="Sources")
                        if collection and collection.name not in col_sources.children:
                            col_sources.children.link(collection)

                        # Exclude collection from all view_layers
                        view_layer: bpy.types.ViewLayer
                        for view_layer in bpy.context.scene.view_layers:
                            recursive_exclude(view_layer.layer_collection, col_sources)
                            collection.hide_render = True
                            # collection.hide_viewport = True

                col = (
                    bpy.data.collections.get(params[input]["name"])
                    if collection is None
                    else collection
                )
                if col:
                    node.inputs["Collection"].default_value = col
            elif params[input]["type"] == "IMAGE" and params[input]["name"]:
                im = bpy.data.images.get(params[input]["name"])
                if im:
                    node.inputs["Image"].default_value = im
            elif params[input]["type"] == "MATERIAL" and params[input]["name"]:
                material = bpy.data.materials.get(params[input]["name"])
                if material:
                    node.inputs["Material"].default_value = material
        else:
            try:
                if hasattr(node.inputs[int(input)], "default_value"):
                    if type(node.inputs[int(input)].default_value) is float:
                        node.inputs[int(input)].default_value = float(params[input])
                    elif type(node.inputs[int(input)].default_value) is int:
                        node.inputs[int(input)].default_value = int(params[input])
                    else:
                        node.inputs[int(input)].default_value = params[input]
            except Exception as e:
                debug("Error setting property: %s" % e)
                debug("Node: %s" % node.name)
                debug("Input: %s" % input)
                debug("Input value: %s" % params[input])
