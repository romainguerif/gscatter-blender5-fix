import bpy
from time import sleep

from ..utils.getters import (
    get_scatter_props,
    get_node_tree,
    get_scene_props,
    get_wm_props,
)
from . import default
from typing import TYPE_CHECKING
from ..slow_task_manager.scopped_slow_task import StartSlowTask
from ..scatter.functions import create_new_system
from ..effects.utils.setter import set_effect_properties
from ..scatter.store import scattersystempresetstore
from ..utils import main_collection

if TYPE_CHECKING:
    from ..effects.props import EffectLayerProps


def get_effect(context, ss, instance_id):
    scatter_props = get_scatter_props(context)
    for scatter_item in scatter_props.scatter_items:
        node_tree = get_node_tree(scatter_item.obj)
        for category in default.EFFECT_CATEGORIES:
            node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
            effects: list[EffectLayerProps] = node.node_tree.gscatter.effects
            for effect in effects:
                if effect.instance_id == instance_id:
                    return effect


def create_system(system, ss, effect_trees):
    si_entry, main_ntree = create_new_system(
        system["name"], ss, system.get("is_terrain", False)
    )
    main_nodes = ["DISTRIBUTION", "SCALE", "ROTATION", "GEOMETRY"]
    for main_node in main_nodes:
        m_node: bpy.types.GeometryNodeGroup = main_ntree.nodes[
            "GScatter"
        ].node_tree.nodes[main_node]
        ntree: bpy.types.GeometryNodeTree = m_node.node_tree
        effect_datas = (
            system["distribution"]
            if main_node == "DISTRIBUTION"
            else system["scale"]
            if main_node == "SCALE"
            else system["rotation"]
            if main_node == "ROTATION"
            else system["geometry"]
        )
        set_effect_properties(effect_datas, ntree, main_node, effect_trees)

    ss.gscatter.scatter_index = len(ss.gscatter.scatter_items) - 1
    si_entry.obj.modifiers["GScatterGeometryNodes"].show_viewport = True
    return si_entry


def add_environment(context, environment, effect_trees: dict) -> None:
    scene_props = get_scene_props(context)
    wm_props = get_wm_props(context)
    starter_props = wm_props.scatter_starter

    with StartSlowTask("Importing dependencies..", 2) as importing_deps:
        importing_deps.set_progress(0)
        importing_deps.set_progress_text("Importing dependencies..")
        importing_deps.refresh()

        # Load data files
        for blend in environment.blends:
            # import materials
            with bpy.data.libraries.load(blend.name) as (
                data_from,
                data_to,
            ):
                data_to.collections = data_from.collections
                data_to.materials = data_from.materials
                data_to.objects = data_from.objects
                data_to.images = data_from.images

        if data_to.objects:
            dep_col = main_collection("GScatter", "Dependencies")
            for ob in data_to.objects:
                dep_col.objects.link(ob)

        bpy.context.view_layer.update()

        importing_deps.set_progress(1)
        importing_deps.set_progress_text("Setting up terrain..")
        importing_deps.refresh()

        if starter_props.terrain_type == "DEFAULT":
            # Create a new plane
            bpy.ops.mesh.primitive_plane_add()
            terrain_main: bpy.types.Object = context.active_object
            terrain_main.name = "Terrain Bounding Plane " + str(
                len(
                    [
                        obj
                        for obj in bpy.data.objects
                        if obj.name.startswith("Terrain Bounding Plane")
                    ]
                )
            )

            terrain_data = environment.environment_dict.get("terrain")
            if terrain_data and terrain_data.get("system"):
                si_entry = create_system(
                    terrain_data["system"], terrain_main, effect_trees
                )
                ss = si_entry.obj

                terrain_main.hide_render = True
                terrain_main.display_type = "WIRE"
            else:
                ss = terrain_main
        elif starter_props.terrain_type == "NEW":
            bpy.ops.mesh.primitive_plane_add()
            terrain_main = context.active_object
            terrain_main.hide_render = True
            terrain_main.display_type = "WIRE"

            terrain_main.name = "Terrain Bounding Plane " + str(
                len(
                    [
                        obj
                        for obj in bpy.data.objects
                        if obj.name.startswith("Terrain Bounding Plane")
                    ]
                )
            )
            system_preset = scattersystempresetstore.get_by_id(
                "system.simple_terrain_generator"
            )

            if starter_props.use_terrain_material:
                for effect in system_preset.geometry:
                    if effect["effect_id"] == "e623fc66b5c243f189bc6276e80f0fe7":
                        terrain_data = environment.environment_dict.get("terrain")
                        if terrain_data:
                            effect["params"]["4"]["name"] = terrain_data["material"]

            terrain_data = system_preset.get_dict()
            si_entry = create_system(terrain_data, terrain_main, effect_trees)
            ss = si_entry.obj
        else:
            ss = starter_props.custom_terrain

        if starter_props.use_terrain_material:
            terrain_data = environment.environment_dict.get("terrain")
            mat = bpy.data.materials.get(terrain_data["material"])
            if ss and mat:
                ss.data.materials.append(mat)

        scene_props.scatter_surface = ss

        # if starter_props.terrain_type == "DEFAULT":
        props = ss.gscatter.environment_props.props
        props.clear()
        for prop in environment.environment_props:
            prop_entry = props.add()
            prop_entry.effect_instance_id = prop.effect_instance_id
            prop_entry.input = prop.input
            prop_entry.input_idx = prop.input_idx
            prop_entry.order_idx = prop.order_idx
            prop_entry.label = prop.input_label

        importing_deps.set_progress(2)
        importing_deps.set_progress_text("Dependencies loaded. Creating systems..")
        importing_deps.refresh()
        sleep(1)

    with StartSlowTask("Adding systems", len(environment.systems)) as system_task:
        for system_idx in range(len(environment.systems)):
            system = environment.systems[system_idx]

            for category in default.EFFECT_CATEGORIES:
                for effect in system[category.lower()]:
                    for param in effect.get("params", {}).keys():
                        prop = environment.get_prop(
                            effect.get("effect_instance_id"), int(param)
                        )
                        if prop is None:
                            continue
                        prop_value = prop.get_prop_value()
                        if prop_value is None:
                            continue
                        effect["params"][param] = {
                            "name": prop_value.name,
                            "type": effect["params"][param]["type"],
                        }

            system_task.set_progress(system_idx)
            system_task.set_progress_text(f"creating system: {system['name']}")
            bpy.context.view_layer.update()
            system_task.refresh()

            si_entry = create_system(system, ss, effect_trees)
            si_entry.color = (
                system.get("color") if system.get("color") else si_entry.color
            )
