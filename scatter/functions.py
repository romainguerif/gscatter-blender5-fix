from random import randint, random
from typing import List

import bpy

from .. import effects
from ..common.props import ScatterItemProps, SceneProps
from ..effects.utils.setter import set_effect_properties
from ..utils import get_preferences, main_collection, recursive_exclude
from ..utils.getters import get_scene_props
from . import default
from .store import scattersystempresetstore


def create_empty_node_tree(name: str) -> bpy.types.GeometryNodeTree:
    group = bpy.data.node_groups.new(type="GeometryNodeTree", name=name)

    if bpy.app.version >= (4, 0, 0):
        group.interface.new_socket(
            socket_type="NodeSocketGeometry", name="Main Geometry", in_out="INPUT"
        )
        group.interface.new_socket(
            socket_type="NodeSocketGeometry", name="Original Geometry", in_out="INPUT"
        )
        group.interface.new_socket(
            socket_type="NodeSocketGeometry", name="Main Geometry", in_out="OUTPUT"
        )
        group.interface.new_socket(
            socket_type="NodeSocketGeometry", name="Original Geometry", in_out="OUTPUT"
        )
    else:
        group.inputs.new("NodeSocketGeometry", "Main Geometry")
        group.inputs.new("NodeSocketGeometry", "Original Geometry")
        group.outputs.new("NodeSocketGeometry", "Main Geometry")
        group.outputs.new("NodeSocketGeometry", "Original Geometry")

    input = group.nodes.new("NodeGroupInput")
    input.name = "Group Input"
    input.location = (0, 0)
    output = group.nodes.new("NodeGroupOutput")
    output.name = "Group Output"
    output.location = (200, 0)

    group.links.new(input.outputs[0], output.inputs[0])
    group.links.new(input.outputs[1], output.inputs[1])

    return group


def create_initial_attribute_values_node_tree() -> bpy.types.GeometryNodeTree:
    return effects.utils.trees.get_effect_nodetree("internal.initial_values")


def create_camera_culling_node_tree() -> bpy.types.GeometryNodeTree:
    return effects.utils.trees.get_effect_nodetree("internal.camera_culling")


def create_viewport_proxy_node_tree() -> bpy.types.GeometryNodeTree:
    return effects.utils.trees.get_effect_nodetree("internal.viewport_proxy")


def create_point_mask_node_tree() -> bpy.types.GeometryNodeTree:
    group = effects.utils.trees.get_effect_nodetree("internal.distribution_mask")

    random_value = group.nodes["Random Value"]
    # Blender reorganised the Random Value node's sockets (Seed was index 8 in 3.x,
    # now the collection only exposes the active data-type sockets). Address by name.
    random_value.inputs["Seed"].default_value = randint(0, 10000)

    return group


def create_main_tree(surface, group) -> bpy.types.GeometryNodeTree:
    main_group = bpy.data.node_groups.new(type="GeometryNodeTree", name="GScatter")

    input = main_group.nodes.new("GeometryNodeObjectInfo")
    input.inputs["Object"].default_value = surface
    input.location = (0, 0)
    input.name = surface.name
    input.transform_space = "RELATIVE"

    join_geom: bpy.types.GeometryNodeGroup = main_group.nodes.new(
        "GeometryNodeJoinGeometry"
    )
    join_geom.name = "Join Geometry"
    join_geom.location = (200, 0)

    system_node: bpy.types.GeometryNodeGroup = main_group.nodes.new("GeometryNodeGroup")
    system_node.node_tree = group
    system_node.name = "GScatter"
    system_node.location = (400, 0)

    if bpy.app.version >= (4, 0, 0):
        main_group.interface.new_socket(
            socket_type="NodeSocketGeometry", name="Geometry", in_out="OUTPUT"
        )
    else:
        main_group.outputs.new("NodeSocketGeometry", "Geometry")

    output = main_group.nodes.new("NodeGroupOutput")
    output.location = (600, 0)

    main_group.links.new(input.outputs["Geometry"], join_geom.inputs[0])
    main_group.links.new(join_geom.outputs[0], system_node.inputs[0])
    main_group.links.new(system_node.outputs[0], output.inputs[0])

    return main_group


def create_scatter_node_trees(
    surface: bpy.types.Object, scatter_item: ScatterItemProps, is_terrain: bool = False
) -> bpy.types.GeometryNodeTree:
    prefs = get_preferences()
    gscatter_props = get_scene_props(bpy.context)
    # scatter_item = surface.gscatter.scatter_items[-1]

    group = bpy.data.node_groups.new(type="GeometryNodeTree", name="GScatter")

    initial_values: bpy.types.GeometryNodeGroup = group.nodes.new("GeometryNodeGroup")
    initial_values.node_tree = create_initial_attribute_values_node_tree()
    initial_values.name = "INITIAL_VALUES"
    initial_values.label = "Initial Values"
    initial_values.location = (400, 0)

    distribution: bpy.types.GeometryNodeGroup = group.nodes.new("GeometryNodeGroup")
    distribution.node_tree = create_empty_node_tree("distribution")
    distribution.name = "DISTRIBUTION"
    distribution.label = "Distribution"
    distribution.location = (600, 0)

    camera_culling_props = gscatter_props.camera_culling
    camera_culling: bpy.types.GeometryNodeGroup = group.nodes.new("GeometryNodeGroup")
    camera_culling.node_tree = create_camera_culling_node_tree()
    camera_culling.name = "CAMERA_CULLING"
    camera_culling.label = "Camera Culling"
    camera_culling.location = (800, 0)
    camera_culling.mute = not camera_culling_props.use
    camera_culling.inputs[1].default_value = camera_culling_props.camera
    camera_culling.inputs[2].default_value = camera_culling_props.focal_length
    camera_culling.inputs[3].default_value = camera_culling_props.sensor_size
    camera_culling.inputs[4].default_value = camera_culling_props.render_width
    camera_culling.inputs[5].default_value = camera_culling_props.render_height
    camera_culling.inputs[6].default_value = camera_culling_props.buffer
    if is_terrain:
        camera_culling.mute = True

    distribution_mask: bpy.types.GeometryNodeGroup = group.nodes.new(
        "GeometryNodeGroup"
    )
    distribution_mask.node_tree = create_point_mask_node_tree()
    distribution_mask.label = "Distribution Mask"
    distribution_mask.location = (1000, 0)

    scale: bpy.types.GeometryNodeGroup = group.nodes.new("GeometryNodeGroup")
    scale.node_tree = create_empty_node_tree("scale")
    scale.name = "SCALE"
    scale.label = "Scale"
    scale.location = (1200, 0)

    rotation: bpy.types.GeometryNodeGroup = group.nodes.new("GeometryNodeGroup")
    rotation.node_tree = create_empty_node_tree("rotation")
    rotation.name = "ROTATION"
    rotation.label = "Rotation"
    rotation.location = (1400, 0)

    geometry: bpy.types.GeometryNodeGroup = group.nodes.new("GeometryNodeGroup")
    geometry.node_tree = create_empty_node_tree("geometry")
    geometry.name = "GEOMETRY"
    geometry.label = "Geometry"
    geometry.location = (1600, 0)

    proxy_settings = gscatter_props.proxy_settings
    viewport_proxy: bpy.types.GeometryNodeGroup = group.nodes.new("GeometryNodeGroup")
    viewport_proxy.node_tree = create_viewport_proxy_node_tree()
    viewport_proxy.name = "VIEWPORT_PROXY"
    viewport_proxy.label = "Viewport Proxy"
    viewport_proxy.location = (1800, 0)
    viewport_proxy.node_tree.nodes["proxy_material"].inputs[
        2
    ].default_value = scatter_item.proxy_mat
    scatter_item.viewport_proxy = prefs.use_proxy_on_new_systems
    scatter_item.obj.display_type = (
        "BOUNDS"
        if proxy_settings.proxy_method == proxy_settings.BOUNDS
        and scatter_item.viewport_proxy
        else "TEXTURED"
    )
    viewport_proxy.mute = (
        True
        if proxy_settings.proxy_method == proxy_settings.BOUNDS
        and scatter_item.viewport_proxy
        else not scatter_item.viewport_proxy
    )
    viewport_proxy.inputs["Point Cloud"].default_value = (
        True if proxy_settings.proxy_method == proxy_settings.POINT_CLOUD else False
    )
    viewport_proxy.inputs["Density"].default_value = proxy_settings.pc_density
    viewport_proxy.inputs["Radius"].default_value = proxy_settings.pc_size

    join_geom: bpy.types.GeometryNodeGroup = group.nodes.new("GeometryNodeJoinGeometry")
    join_geom.name = "Join Geometry"
    join_geom.location = (2000, 0)

    if bpy.app.version >= (4, 0, 0):
        group.interface.new_socket(
            socket_type="NodeSocketGeometry", name="Geometry", in_out="OUTPUT"
        )
    else:
        group.outputs.new("NodeSocketGeometry", "Geometry")
    output = group.nodes.new("NodeGroupOutput")
    output.name = "Group Output"
    output.location = (2200, 0)

    if bpy.app.version >= (4, 0, 0):
        group.interface.new_socket(
            socket_type="NodeSocketGeometry", name="Geometry", in_out="INPUT"
        )
    else:
        group.inputs.new("NodeSocketGeometry", "Geometry")
    input_node = group.nodes.new("NodeGroupInput")
    input_node.location = (0, 0)

    group.links.new(input_node.outputs[0], initial_values.inputs[0])
    group.links.new(initial_values.outputs[0], distribution.inputs[0])
    group.links.new(initial_values.outputs[0], distribution.inputs[1])
    group.links.new(distribution.outputs[0], camera_culling.inputs[0])
    group.links.new(camera_culling.outputs[0], distribution_mask.inputs[0])
    group.links.new(distribution_mask.outputs[0], scale.inputs[0])
    group.links.new(scale.outputs[0], rotation.inputs[0])
    group.links.new(rotation.outputs[0], geometry.inputs[0])
    group.links.new(geometry.outputs[0], viewport_proxy.inputs[0])
    group.links.new(viewport_proxy.outputs[0], join_geom.inputs[0])
    group.links.new(join_geom.outputs[0], output.inputs[0])

    group.links.new(distribution.outputs[1], scale.inputs[1])
    group.links.new(scale.outputs[1], rotation.inputs[1])
    group.links.new(rotation.outputs[1], geometry.inputs[1])

    main_group = create_main_tree(surface, group)
    return main_group


def create_new_system(name: str, ss: bpy.types.Object, is_terrain: bool = False):
    mesh = bpy.data.meshes.new(name)
    o = bpy.data.objects.new(name, mesh)
    color = (random(), random(), random(), 1)
    o.color = color
    o.gscatter.ss = ss
    proxy_mat = bpy.data.materials.new(name=f"proxy_{name}")
    proxy_mat.diffuse_color = color

    col_systems = main_collection(sub="Systems")
    # collection = bpy.data.collections.new(name) # TODO Wrap System in a Collection for deactivating being able to toggle it in the viewlayer - other scenes
    # col_systems.children.link(collection)
    col_systems.objects.link(o)

    si_entry = ss.gscatter.scatter_items.add()
    si_entry.obj = o
    si_entry.color = color
    si_entry.proxy_mat = proxy_mat
    si_entry.ntree_version = default.NODETREE_VERSION
    si_entry.is_terrain = is_terrain

    m: bpy.types.NodesModifier = o.modifiers.new(
        type="NODES", name="GScatterGeometryNodes"
    )
    main_ntree = create_scatter_node_trees(ss, si_entry, is_terrain)
    m.node_group = main_ntree
    o.gscatter.is_gscatter_system = True
    return si_entry, main_ntree


def scatter_objects(
    objects: List[bpy.types.Object],
    individual: bool,
    preset_id: str,
    is_gscatter_asset: bool = False,
):
    """Scatter a list of objects, either together or individually."""
    # col_sources = main_collection(sub='Sources')
    # scattered = set(col_sources.all_objects)
    objects = list(objects)

    # for index, obj in enumerate(objects):
    #     if obj in scattered:
    #         obj = obj.copy()
    #         objects[index] = obj
    #         #obj.hide_set(True)

    if individual:
        for obj in objects:
            col_name = f"{obj.name}"

            col_new = bpy.data.collections.new(f"{col_name}")
            if is_gscatter_asset:
                col_new.gscatter.is_gscatter_asset = True
                name_split = col_name.split("_")
                col_new.gscatter.asset_id = name_split[0] + "_" + name_split[1]

            # for oldcol in obj.users_collection: # TODO Unlinking management needs fixing
            #     oldcol.objects.unlink(obj)

            col_new.objects.link(obj)

            scatter_collection(col_new, preset_id)

    else:
        col_name = f"{objects[0].name} {len(objects) if len(objects) > 1 else ''}"
        col = bpy.data.collections.get(col_name)
        if col:
            col_name = (
                col.name
                + f" {len([c for c in bpy.data.collections if c.name.startswith(col_name)])}"
            )

        col_new = bpy.data.collections.new(f"{col_name}")

        for obj in objects:
            # for oldcol in obj.users_collection: # TODO Unlinking management needs fixing
            #     oldcol.objects.unlink(obj)
            col_new.objects.link(obj)

        scatter_collection(col_new, preset_id)


def scatter_collection(collection: bpy.types.Collection, preset_id: str):
    """Create a scatter system for the given collection."""
    col_sources = main_collection(sub="Sources")
    system_preset = scattersystempresetstore.get_by_id(preset_id)

    if collection:
        # Exclude collection from all view_layers
        view_layer: bpy.types.ViewLayer
        for view_layer in bpy.context.scene.view_layers:
            recursive_exclude(view_layer.layer_collection, col_sources)
            collection.hide_render = True
            # collection.hide_viewport = True

        if collection.name not in col_sources.children:
            col_sources.children.link(collection)

    G: SceneProps = bpy.context.scene.gscatter
    ss: bpy.types.Object = G.scatter_surface

    name = (
        f"{collection.name.split(':')[0]}" + " : System"
        if collection
        else system_preset.name + " : System"
    )
    _, main_ntree = create_new_system(name, ss, system_preset.is_terrain)

    main_nodes = ["DISTRIBUTION", "SCALE", "ROTATION", "GEOMETRY"]
    effect_trees = dict()
    for main_node in main_nodes:
        m_node: bpy.types.GeometryNodeGroup = main_ntree.nodes[
            "GScatter"
        ].node_tree.nodes[main_node]
        ntree: bpy.types.GeometryNodeTree = m_node.node_tree
        effect_datas = (
            system_preset.distribution
            if main_node == "DISTRIBUTION"
            else system_preset.scale
            if main_node == "SCALE"
            else system_preset.rotation
            if main_node == "ROTATION"
            else system_preset.geometry
        )

        set_effect_properties(
            effect_datas, ntree, main_node, effect_trees, collection=collection
        )

    ss.gscatter.scatter_index = len(ss.gscatter.scatter_items) - 1

    # Reselect Scatter Surface
    bpy.ops.object.select_all(action="DESELECT")
    ss.select_set(True)
    bpy.context.view_layer.objects.active = ss
