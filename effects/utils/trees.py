from typing import Union

import bpy

from ...utils.getters import get_node_tree, get_scene_props
from .. import default
from ..store import effectstore
from ..store.utils import get_input_from_identifier


def get_effect_nodetree(
    id: str, version: Union[list[int], None] = None
) -> Union[bpy.types.GeometryNodeTree, None]:
    if version is None:
        effect = effectstore.get_newest_by_id(id)
    else:
        effect = effectstore.get_by_id_and_version(id, version)
    if effect:
        return effect.nodetree
    else:
        return None


def prev_node(node: bpy.types.GeometryNode) -> bpy.types.GeometryNode:
    return node.inputs[0].links[0].from_node


def next_node(node: bpy.types.GeometryNode) -> bpy.types.GeometryNode:
    return node.outputs[0].links[0].to_node


def has_next_node(node: bpy.types.GeometryNode) -> bpy.types.GeometryNode:
    socket = next(
        (
            socket
            for socket in node.outputs
            if isinstance(socket, bpy.types.NodeSocketGeometry)
        ),
        None,
    )
    return socket and socket.is_linked


def get_node_with_visualization(node_new: bpy.types.GeometryNode, mode: str):
    if mode == "BEFORE":
        node_prev = prev_node(node_new)
        if not node_prev.mute and node_prev.outputs.get("Original Geometry"):
            return node_prev
        if node_prev.type != "GROUP_INPUT":
            node_prev = get_node_with_visualization(node_prev, mode)
            return node_prev
    else:
        node_next = next_node(node_new)
        if not node_next.mute and node_next.inputs.get("Original Geometry"):
            return node_next
        if node_next.type != "GROUP_OUTPUT":
            node_next = get_node_with_visualization(node_next, mode)
            return node_next


def connect_visualization_input_outputs(
    node: bpy.types.GeometryNode, node_tree: bpy.types.GeometryNodeTree
):
    prev_viz_node_for_new_node = get_node_with_visualization(node, "BEFORE")
    next_viz_node_for_new_node = get_node_with_visualization(node, "AFTER")

    if prev_viz_node_for_new_node and next_viz_node_for_new_node:
        prev_output = prev_viz_node_for_new_node.outputs.get("Original Geometry")
        next_input = next_viz_node_for_new_node.inputs.get("Original Geometry")
        new_node_output = node.outputs.get("Original Geometry")
        new_node_input = node.inputs.get("Original Geometry")
        if prev_output and new_node_input:
            if prev_output.is_linked:
                node_tree.links.remove(prev_output.links[0])
            node_tree.links.new(output=prev_output, input=new_node_input)
        if new_node_output and next_input:
            if new_node_output.is_linked:
                node_tree.links.remove(new_node_output.links[0])
            node_tree.links.new(output=new_node_output, input=next_input)


def insert_before(
    node_new: bpy.types.GeometryNode,
    node_next: bpy.types.GeometryNode,
    node_tree: bpy.types.GeometryNodeTree,
):
    node_prev = prev_node(node_next)
    node_tree.links.remove(node_prev.outputs[0].links[0])
    node_tree.links.new(node_prev.outputs[0], node_new.inputs[0])
    node_tree.links.new(node_new.outputs[0], node_next.inputs[0])

    connect_visualization_input_outputs(node_new, node_tree)
    connect_visualization_input_outputs(node_next, node_tree)


def insert_after(
    node_new: bpy.types.GeometryNode,
    node_prev: bpy.types.GeometryNode,
    node_tree: bpy.types.GeometryNodeTree,
):
    node_next = next_node(node_prev)
    node_tree.links.remove(node_prev.outputs[0].links[0])
    node_tree.links.new(node_prev.outputs[0], node_new.inputs[0])
    node_tree.links.new(node_new.outputs[0], node_next.inputs[0])

    connect_visualization_input_outputs(node_new, node_tree)
    connect_visualization_input_outputs(node_prev, node_tree)


def insert_end(node_new: bpy.types.GeometryNode, node_tree: bpy.types.GeometryNodeTree):
    node_last = next(
        node for node in node_tree.nodes if isinstance(node, bpy.types.NodeGroupOutput)
    )
    node_prev = prev_node(node_last)
    node_tree.links.remove(node_prev.outputs[0].links[0])
    node_tree.links.new(node_prev.outputs[0], node_new.inputs[0])
    node_tree.links.new(node_new.outputs[0], node_last.inputs[0])

    connect_visualization_input_outputs(node_new, node_tree)


def disconnect_node(
    node: bpy.types.GeometryNode, node_tree: bpy.types.GeometryNodeTree
) -> bpy.types.GeometryNode:
    """Disconnects node at index from the nodetree chain, returns said node.
    param : Index - index of the node relative to the first node in the chain
    Assume: there is only Geometry <-> Geometry between nodes
    """
    node_prev = prev_node(node)
    node_next = next_node(node)

    prev_viz_node = get_node_with_visualization(node, mode="BEFORE")
    next_viz_node = get_node_with_visualization(node, mode="AFTER")
    node_tree.links.new(
        input=next_viz_node.inputs["Original Geometry"],
        output=prev_viz_node.outputs["Original Geometry"],
    )

    node_tree.links.remove(node.inputs[0].links[0])
    node_tree.links.remove(node.outputs[0].links[0])
    node_tree.links.new(node_prev.outputs[0], node_next.inputs[0])

    return node


def deepcopy_nodetree(
    node_tree: bpy.types.GeometryNodeTree,
) -> bpy.types.GeometryNodeTree:
    new_tree: bpy.types.GeometryNodeTree = node_tree.copy()
    for node in new_tree.nodes.values():
        if isinstance(node, bpy.types.GeometryNodeGroup):
            node.node_tree = deepcopy_nodetree(node.node_tree)
    return new_tree


def layout_nodetree(node_tree: bpy.types.GeometryNodeTree, first_node=None):
    """This function expects the node tree to be a chain of nodes."""
    if first_node is None:
        node = next(
            node
            for node in node_tree.nodes
            if isinstance(node, bpy.types.NodeGroupInput)
        )
    else:
        node = first_node
    x = 200
    while has_next_node(node):
        node = next_node(node)
        node.location = (x, 0)
        x += 200


def connect_last_node_to_visualize_output(main_tree: bpy.types.GeometryNodeTree):
    # Connect Distribute effect outputs
    dist_node = main_tree.nodes["DISTRIBUTION"]
    output_node = get_group_output_node(dist_node.node_tree)
    last_effect_node = get_node_with_visualization(output_node, "BEFORE")
    last_effect_geom_output = last_effect_node.outputs.get("Original Geometry")
    if len(last_effect_geom_output.links) == 0:
        dist_node.node_tree.links.new(
            input=output_node.inputs[1], output=last_effect_geom_output
        )

    # Connect SCALE effect outputs
    scale_node = main_tree.nodes["SCALE"]
    output_node = get_group_output_node(scale_node.node_tree)
    last_effect_node = get_node_with_visualization(output_node, "BEFORE")
    last_effect_geom_output = last_effect_node.outputs.get("Original Geometry")
    if len(last_effect_geom_output.links) == 0:
        scale_node.node_tree.links.new(
            output=last_effect_geom_output, input=output_node.inputs[1]
        )


def disconnect_all_geometry_outputs(context):
    for obj in context.view_layer.objects:
        item_tree = get_node_tree(obj)
        if item_tree:
            item_geom_node = item_tree.nodes.get("GEOMETRY")
            geom_viz_output = item_geom_node.outputs.get("Original Geometry")
            if geom_viz_output and geom_viz_output.is_linked:
                item_tree.links.remove(geom_viz_output.links[0])


def disconnect_main_geometry(item_obj):
    item_tree = get_node_tree(item_obj)
    if item_tree:
        dist_node: bpy.types.GeometryNode = item_tree.nodes.get("DISTRIBUTION")
        if len(dist_node.inputs["Main Geometry"].links) > 0:
            link = dist_node.inputs["Main Geometry"].links[0]
            item_tree.links.remove(link)


def connect_main_geometry(item_obj):
    item_tree = get_node_tree(item_obj)
    if item_tree:
        dist_node: bpy.types.GeometryNode = item_tree.nodes.get("DISTRIBUTION")
        initial_node: bpy.types.GeometryNode = item_tree.nodes.get("INITIAL_VALUES")
        item_tree.links.new(
            output=initial_node.outputs[0], input=dist_node.inputs["Main Geometry"]
        )


def set_channel_input(group_node: bpy.types.GeometryNode, category: str):
    if group_node.inputs.get(default.INPUT_CHANNEL) is not None:
        group_node.inputs[default.INPUT_CHANNEL].default_value = category.lower()


def is_node_tree_valid(node_tree: bpy.types.GeometryNodeTree):
    main_output = get_group_output_node(node_tree).inputs.get("Main Geometry")
    original_output = get_group_output_node(node_tree).inputs.get("Original Geometry")

    if main_output is None or original_output is None:
        return False

    return main_output.is_linked and original_output.is_linked


def get_node_by_type(node_tree: bpy.types.GeometryNodeTree, node_type: str):
    for node in node_tree.nodes:
        if node.type == node_type:
            return node


def get_group_input_node(node_tree: bpy.types.GeometryNodeTree):
    return get_node_by_type(node_tree, "GROUP_INPUT")


def get_group_output_node(node_tree: bpy.types.GeometryNodeTree):
    return get_node_by_type(node_tree, "GROUP_OUTPUT")


def create_mix_inputs(effect):
    influence_input = effect.group_node.inputs.get(default.INPUT_INFLUENCE)
    blendtype_input = effect.group_node.inputs.get(default.INPUT_BLEND_TYPE)
    invert_input = effect.group_node.inputs.get(default.INPUT_INVERT)

    if influence_input is None:
        effect.group_node.node_tree.inputs.new(
            type="NodeSocketFloat", name=default.INPUT_INFLUENCE
        )
        influence_input = effect.group_node.inputs.get(default.INPUT_INFLUENCE)
    influence_input.default_value = effect.influence / 100

    if blendtype_input is None:
        effect.group_node.node_tree.inputs.new(
            type="NodeSocketString", name=default.INPUT_BLEND_TYPE
        )
        blendtype_input = effect.group_node.inputs.get(default.INPUT_BLEND_TYPE)
    blendtype_input.default_value = effect.blend_type

    if invert_input is None:
        effect.group_node.node_tree.inputs.new(
            type="NodeSocketBool", name=default.INPUT_INVERT
        )
        invert_input = effect.group_node.inputs.get(default.INPUT_INVERT)
    invert_input.default_value = effect.invert


def update_subivide_node(main_tree: bpy.types.GeometryNodeTree):
    subdivide_node = main_tree.nodes.get("subdivide_mesh")
    scene_props = get_scene_props(bpy.context)
    if subdivide_node is None:
        node = main_tree.nodes.new("GeometryNodeSubdivideMesh")
        node.name = "subdivide_mesh"
        node.label = "Subdivide"
        node.location = (600, -200)

        level = get_input_from_identifier(node.inputs, "Level")
        level.default_value = scene_props.visualization_resolution - 1

        initial_values = main_tree.nodes.get("INITIAL_VALUES")
        distribution_node = main_tree.nodes.get("DISTRIBUTION")

        main_tree.links.new(output=initial_values.outputs[0], input=node.inputs[0])
        main_tree.links.new(
            output=node.outputs[0], input=distribution_node.inputs["Original Geometry"]
        )
    else:
        level = get_input_from_identifier(subdivide_node.inputs, "Level")
        if level.default_value != scene_props.visualization_resolution - 1:
            level.default_value = scene_props.visualization_resolution - 1


def create_template_effect_node_tree() -> bpy.types.GeometryNodeTree:
    return get_effect_nodetree("internal.template_effect")


def create_placeholder_effect_node_tree() -> bpy.types.GeometryNodeTree:
    return get_effect_nodetree("internal.placeholder_effect")


def create_visualization_node_tree() -> bpy.types.GeometryNodeTree:
    return get_effect_nodetree("internal.vizualizer")


def create_mixer_node_tree() -> bpy.types.GeometryNodeTree:
    return get_effect_nodetree("internal.mixer")


def add_effect_to_placeholder(
    placeholder_tree: bpy.types.GeometryNodeTree,
    effect_ntree: bpy.types.GeometryNodeTree,
):
    effect_node: bpy.types.GeometryNodeGroup = placeholder_tree.nodes.new(
        "GeometryNodeGroup"
    )
    effect_node.node_tree = effect_ntree
    effect_node.name = "effect"
    effect_node.label = effect_ntree.name
    effect_node.location = (200, 0)

    grp_input_node = placeholder_tree.nodes["Group Input"]
    grp_output_node = placeholder_tree.nodes["Group Output"]
    visualizer_node = placeholder_tree.nodes["visualizer"]

    if hasattr(effect_node, "inputs") and any(
        socket.name == "Geometry" or socket.name == "Main Geometry"
        for socket in effect_node.inputs
    ):
        socket_name = (
            "Main Geometry"
            if any(socket.name == "Main Geometry" for socket in effect_node.inputs)
            else "Geometry"
        )

        placeholder_tree.links.new(
            output=grp_input_node.outputs["Main Geometry"],
            input=effect_node.inputs[socket_name],
        )

        placeholder_tree.links.new(
            output=effect_node.outputs[socket_name],
            input=grp_output_node.inputs["Main Geometry"],
        )
        placeholder_tree.links.new(
            output=grp_input_node.outputs["Original Geometry"],
            input=grp_output_node.inputs["Original Geometry"],
        )

        if any(socket.name == "Original Geometry" for socket in effect_node.inputs):
            placeholder_tree.links.new(
                output=grp_input_node.outputs["Original Geometry"],
                input=effect_node.inputs["Original Geometry"],
            )

            placeholder_tree.links.new(
                output=effect_node.outputs["Original Geometry"],
                input=grp_output_node.inputs["Original Geometry"],
            )

        if any(socket.name == "data" for socket in effect_node.outputs):
            placeholder_tree.links.new(
                output=effect_node.outputs[socket_name],
                input=visualizer_node.inputs["Main Geometry"],
            )
            placeholder_tree.links.new(
                output=effect_node.outputs["Original Geometry"],
                input=visualizer_node.inputs["Original Geometry"],
            )
            placeholder_tree.links.new(
                output=effect_node.outputs["data"], input=visualizer_node.inputs["Data"]
            )

            placeholder_tree.links.new(
                output=visualizer_node.outputs["Main Geometry"],
                input=grp_output_node.inputs["Main Geometry"],
            )
            placeholder_tree.links.new(
                output=visualizer_node.outputs["Original Geometry"],
                input=grp_output_node.inputs["Original Geometry"],
            )
        else:
            placeholder_tree.nodes.remove(visualizer_node)

        # Connect mix, influence and invert inputs
        if effect_node.inputs.get(default.INPUT_BLEND_TYPE):
            placeholder_tree.links.new(
                output=grp_input_node.outputs[default.INPUT_BLEND_TYPE],
                input=effect_node.inputs[default.INPUT_BLEND_TYPE],
            )
            placeholder_tree.links.new(
                output=grp_input_node.outputs[default.INPUT_INFLUENCE],
                input=effect_node.inputs[default.INPUT_INFLUENCE],
            )
            placeholder_tree.links.new(
                output=grp_input_node.outputs[default.INPUT_INVERT],
                input=effect_node.inputs[default.INPUT_INVERT],
            )

    layout_nodetree(placeholder_tree)
