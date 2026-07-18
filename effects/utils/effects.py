from typing import TYPE_CHECKING, List

import bpy

from ...utils.logger import info
from ..store import effectstore
from . import trees
from ...utils.getters import (
    get_wm_props,
    get_node_tree,
    get_scatter_item,
    get_scene_props,
)
from ...utils import main_collection
from uuid import uuid4
from .. import default

if TYPE_CHECKING:
    from ..props import EffectLayerProps

cache_vals = []


def get_placeholders() -> bpy.types.GeometryNodeTree:
    if "GSCATTER_Placeholders" in bpy.data.node_groups:
        return bpy.data.node_groups["GSCATTER_Placeholders"]

    group = bpy.data.node_groups.new(
        type="GeometryNodeTree", name="GSCATTER_Placeholders"
    )

    try:
        group.inputs.new("NodeSocketGeometry", "Geometry")
        group.outputs.new("NodeSocketGeometry", "Geometry")
    except Exception:
        group.interface.new_socket(
            socket_type="NodeSocketGeometry", name="Geometry", in_out="INPUT"
        )
        group.interface.new_socket(
            socket_type="NodeSocketGeometry", name="Geometry", in_out="OUTPUT"
        )

    input = group.nodes.new("NodeGroupInput")
    group.nodes.new("ShaderNodeMixRGB")
    output = group.nodes.new("NodeGroupOutput")
    group.links.new(input.outputs[0], output.inputs[0])

    return group


def add_effect(
    effect_ntree: bpy.types.GeometryNodeTree,
    dst_ntree: bpy.types.GeometryNodeTree,
    category: str,
    effect_id: str,
    effect_version: list[int],
    instance_id: str = None,
    new: bool = True,
) -> "EffectLayerProps":
    """Adds an effect to the given nodetree at the requested index"""
    new_node: bpy.types.GeometryNodeGroup = dst_ntree.nodes.new("GeometryNodeGroup")
    new_node.node_tree = effect_ntree

    effect: "EffectLayerProps" = dst_ntree.gscatter.effects.add()
    effect.name = str(dst_ntree.gscatter.next_id)
    effect_data = effectstore.get_by_id_and_version(effect_id, effect_version)
    effect.icon = effect_data.icon
    effect.blend_types = effect_data.blend_types
    effect.blend_type = effect_data.default_blend_type
    effect.instance_id = instance_id if instance_id else str(uuid4())

    effect_ntree.gscatter.category = effect_data.categories
    effect_ntree.gscatter.icon = effect_data.icon
    effect_ntree.gscatter.effect_id = effect_id
    effect_ntree.gscatter.version = effect_version

    if new:
        ntree_name = effect_ntree.name.replace("_main", "")
        effect_ntree.name += "_main"
        placeholder_effect = trees.create_placeholder_effect_node_tree()
        placeholder_effect.name = ntree_name
        trees.add_effect_to_placeholder(placeholder_effect, effect_ntree)
        new_node.node_tree = placeholder_effect
        effect_ntree = placeholder_effect

    dst_ntree.gscatter.next_id += 1
    new_node.name = f"{effect.name}_group"
    new_node.label = effect_data.name

    trees.set_channel_input(effect.group_node, category)
    trees.create_mix_inputs(effect)

    scene_props = get_scene_props()
    if effect_id == "system.distribute_on_faces":
        effect.effect_node.inputs[
            4
        ].default_value = scene_props.viewport_display_percentage

    select_effect(effect.name, dst_ntree)

    effect_ntree.gscatter.is_gscatter_effect = True
    effect_ntree.gscatter.category = effect_data.categories
    effect_ntree.gscatter.effect_id = effect_id
    effect_ntree.gscatter.version = effect_version

    trees.insert_end(new_node, dst_ntree)
    trees.layout_nodetree(dst_ntree)
    return effect


def duplicate_effect(
    dst_ntree: bpy.types.GeometryNodeTree,
    category: str,
    ref_effect: "EffectLayerProps",
) -> "EffectLayerProps":
    effect_ntree = trees.deepcopy_nodetree(ref_effect.effect_node.node_tree)
    dst_effect = add_effect(
        effect_ntree,
        dst_ntree,
        category,
        ref_effect.get_effect_id(),
        ref_effect.get_effect_version(),
    )

    ref_grp = ref_effect.effect_node
    dst_grp = dst_effect.effect_node
    for i in range(len(ref_grp.inputs)):
        if hasattr(ref_grp.inputs[i], "default_value"):
            dst_grp.inputs[i].default_value = ref_grp.inputs[i].default_value
    trees.set_channel_input(dst_effect.group_node, category)
    return dst_effect


def move_effect(effect_name: str, node_tree: bpy.types.GeometryNodeTree, up: bool):
    """Moves an effect in the given nodetree forward or backward"""
    effects: bpy.types.bpy_prop_collection = node_tree.gscatter.effects
    src_index = effects.find(effect_name)
    node = effects.get(effect_name).group_node

    if up:
        dst_index = src_index + 1
        next_node = trees.next_node(node)
        trees.disconnect_node(node, node_tree)
        trees.insert_after(node, next_node, node_tree)
    else:
        dst_index = src_index - 1
        prev_node = trees.prev_node(node)
        trees.disconnect_node(node, node_tree)
        trees.insert_before(node, prev_node, node_tree)

    effects.move(src_index, dst_index)
    trees.layout_nodetree(node_tree)


def delete_effect(effect_name: str, node_tree: bpy.types.GeometryNodeTree):
    effects: bpy.types.bpy_prop_collection = node_tree.gscatter.effects
    effect: "EffectLayerProps" = effects.get(effect_name)
    node = effect.group_node
    node_tree.nodes.remove(trees.disconnect_node(node, node_tree))
    index = effects.find(effect_name)
    effects.remove(index)
    if len(effects) > 0:
        effect = effects[-1]
        select_effect(effect.name, node_tree)

    trees.layout_nodetree(node_tree)


def select_effect(effect_name: str, node_tree: bpy.types.GeometryNodeTree):
    effects: List["EffectLayerProps"] = node_tree.gscatter.effects

    for effect in effects:
        effect.selected = effect.name == effect_name


def toggle_visualization(node_tree):
    info("Toggling visualization")
    scene_props = get_scene_props(bpy.context)
    category = scene_props.active_category
    node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
    effect: "EffectLayerProps" = node.node_tree.gscatter.get_selected()

    if scene_props.visualize_mode == "SELECTED":
        for cat in ["DISTRIBUTION", "SCALE"]:
            nod: bpy.types.GeometryNodeGroup = node_tree.nodes[cat]
            effects: List["EffectLayerProps"] = nod.node_tree.gscatter.effects
            for eff in effects:
                if eff != effect:
                    viz_input = eff.group_node.inputs.get(default.INPUT_VISUALIZING)
                    if viz_input and viz_input.default_value:
                        viz_input.default_value = False

        viz_input = effect.group_node.inputs.get(default.INPUT_VISUALIZING)
        if viz_input and not viz_input.default_value:
            viz_input.default_value = True
    elif scene_props.visualize_mode == "ALL":
        for cat in ["DISTRIBUTION", "SCALE"]:
            nod: bpy.types.GeometryNodeGroup = node_tree.nodes[cat]
            effects: List["EffectLayerProps"] = nod.node_tree.gscatter.effects
            for eff in effects:
                viz_input = eff.group_node.inputs.get(default.INPUT_VISUALIZING)
                if viz_input and viz_input.default_value and cat != category:
                    viz_input.default_value = False
                elif viz_input and not viz_input.default_value:
                    viz_input.default_value = cat == category
    else:
        for cat in ["DISTRIBUTION", "SCALE"]:
            nod: bpy.types.GeometryNodeGroup = node_tree.nodes[cat]
            effects: List["EffectLayerProps"] = nod.node_tree.gscatter.effects
            for eff in effects:
                viz_input = eff.group_node.inputs.get(default.INPUT_VISUALIZING)
                if viz_input and viz_input.default_value:
                    viz_input.default_value = False

    obj = scene_props.scatter_surface
    if obj.gscatter.is_terrain:
        obj = obj.gscatter.ss if obj.gscatter.ss else obj

    if obj and category in ["DISTRIBUTION", "SCALE"]:
        if scene_props.visualize_mode != "OFF":
            name = category.lower() + "_visualizer"
            color_layer = obj.data.vertex_colors.get(name)
            if color_layer is None:
                color_layer = obj.data.vertex_colors.new(name=name, do_init=False)
                # color_layer.name = name
            if obj.data.attributes.active_color != obj.data.attributes[name]:
                obj.data.attributes.active_color = obj.data.attributes[name]
                obj.data.vertex_colors[name].active = True
                obj.data.vertex_colors[name].active_render = True


def reset_colors():
    scene_props = get_scene_props(bpy.context)
    get_wm_props(bpy.context)
    obj = scene_props.scatter_surface
    if obj.gscatter.is_terrain:
        obj = obj.gscatter.ss if obj.gscatter.ss else obj
    if obj:
        names = ["distribution_visualizer", "scale_visualizer"]
        for name in names:
            color_layer = obj.data.vertex_colors.get(name)
            if color_layer:
                obj.data.vertex_colors.remove(color_layer)


def clear_cache():
    global cache_vals
    cache_vals.clear()


def can_visualize_selected_effect(context, main_tree=None):
    scene_props = get_scene_props(bpy.context)
    item = get_scatter_item(bpy.context)
    category = scene_props.active_category
    if main_tree is None:
        main_tree = get_node_tree(bpy.context)
    if main_tree is None:
        return False
    node: bpy.types.GeometryNodeGroup = main_tree.nodes[category]

    if not (
        item
        and item.get_ntree_version() >= (2, 1, 0)
        and category in ["DISTRIBUTION", "SCALE"]
    ):
        return False

    effect: "EffectLayerProps" = node.node_tree.gscatter.get_selected()
    if not (effect and effect.effect_node):
        return False
    if effect.group_node.mute:
        return False

    visualizer_node = effect.group_node.node_tree.nodes.get("visualizer")

    if visualizer_node:
        data_input: bpy.types.NodeSocket = visualizer_node.inputs.get("Data")
        if data_input is not None and data_input.is_linked:
            return True
    return False


def create_viz_node_tree(
    main_tree: bpy.types.GeometryNodeTree, ss: bpy.types.Object, si: bpy.types.Object
) -> bpy.types.GeometryNodeTree:
    """Creates a viz node tree for given scatter item"""
    obj_name = "gscatter_viz_obj"
    viz_obj = bpy.data.objects.get(obj_name)
    if viz_obj is None:
        viz_obj = bpy.data.objects.new(
            name=obj_name, object_data=bpy.data.meshes.new(obj_name)
        )
    main = main_collection()
    col = main_collection(sub="Visualizer")
    for view_layer in bpy.context.scene.view_layers:
        view_layer.layer_collection.children[main.name].children[
            col.name
        ].exclude = False
    if viz_obj.name not in col.objects:
        col.objects.link(viz_obj)

    viz_copy_name = si.obj.name + "_viz_copy"
    viz_copy_tree = bpy.data.node_groups.get(viz_copy_name)
    if viz_copy_tree is None:
        viz_copy_tree: bpy.types.GeometryNodeTree = main_tree.copy()
        viz_copy_tree.name = viz_copy_name
        viz_output_node = viz_copy_tree.nodes["Group Output"]
        geom_node = viz_copy_tree.nodes.get("GEOMETRY")
        viz_copy_tree.links.new(
            input=viz_output_node.inputs[0], output=geom_node.outputs[1]
        )

        join_geom: bpy.types.GeometryNodeGroup = viz_copy_tree.nodes.new(
            "GeometryNodeJoinGeometry"
        )
        join_geom.name = "Join System"
        join_geom.location = (200, 0)

        input = viz_copy_tree.nodes.new("GeometryNodeObjectInfo")
        input.inputs[0].default_value = ss
        input.location = (0, 0)
        input.name = ss.name
        input.transform_space = "RELATIVE"
        initial_value_node = viz_copy_tree.nodes.get("INITIAL_VALUES")

        viz_copy_tree.links.new(
            input=join_geom.inputs[0], output=input.outputs["Geometry"]
        )
        viz_copy_tree.links.new(
            input=initial_value_node.inputs[0], output=join_geom.outputs["Geometry"]
        )

    trees.update_subivide_node(viz_copy_tree)

    # Create viz_modifier in scatter surface
    mod_name = "gscater_viz_modifier"
    mod = viz_obj.modifiers.get(mod_name)
    if mod is None:
        mod = viz_obj.modifiers.new(name=mod_name, type="NODES")
    mod.node_group = viz_copy_tree
    return viz_copy_tree


def update_viz_surfaces(viz_copy_tree, join_geom_main, join_geom_viz, surfaces_hidden):
    """Checks if the linked surfaces have changed and updates the viz tree accordingly"""
    if len(join_geom_main.inputs[0].links) != len(join_geom_viz.inputs[0].links):
        for link in join_geom_viz.inputs[0].links:
            viz_copy_tree.nodes.remove(link.from_node)

        for link in join_geom_main.inputs[0].links:
            input = viz_copy_tree.nodes.new("GeometryNodeObjectInfo")
            input.inputs[0].default_value = link.from_node.inputs[0].default_value
            input.location = [0, link.from_node.location[1]]
            input.name = link.from_node.inputs[0].default_value.name
            input.transform_space = "RELATIVE"
            viz_copy_tree.links.new(
                input=join_geom_viz.inputs[0], output=input.outputs["Geometry"]
            )

        for surface in surfaces_hidden:
            try:
                surface.hide_set(False)
            except Exception:
                continue
        surfaces_hidden.clear()
        for link in viz_copy_tree.nodes["Join System"].inputs[0].links:
            system = link.from_node.inputs[0].default_value
            system.hide_set(True)
            surfaces_hidden.append(system)
