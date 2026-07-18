import pathlib
from os.path import dirname, join
from typing import TYPE_CHECKING, Any, Tuple, Union
from uuid import uuid4

import bpy
from bpy.types import Context, Depsgraph, GeometryNodeTree, NodesModifier, Object
import addon_utils

from .. import __package__ as base_package

FLOAT_MIN = -1e20
FLOAT_MAX = 1e20

# TODO: Import these once we drop 2.93 support.
NON_PRIMITIVE_SOCKETS = {
    "NodeSocketGeometry",
    "NodeSocketTexture",
}


def clean(value: Any) -> Union[str, list, Any, None]:
    """Cleans arbitrary datatypes for conversion to string."""
    if isinstance(value, str):
        return value
    if hasattr(value, "__len__"):
        return list(value)
    if hasattr(value, "__add__"):
        return value
    return None


if TYPE_CHECKING:
    from ..common.prefs import GScatterPreferences
    from ..common.props import (
        ObjectProps,
        ScatterItemProps,
        SceneProps,
        WindowManagerProps,
    )


def get_package() -> str:
    if bpy.app.version >= (4, 2, 0):
        return base_package
    else:
        return __package__.split(".")[-2]


def get_version() -> Tuple[int, int, int]:
    version = [
        [str(i) for i in addon.bl_info.get("version", (0, 0, 0))]
        for addon in addon_utils.modules()
        if addon.__name__ == get_package()
    ][0]
    return version


def get_addon_dir():
    return pathlib.Path(__file__).parent.parent


def get_preferences(source: Context = None) -> "GScatterPreferences":
    source = source if source else bpy.context
    return bpy.context.preferences.addons[get_package()].preferences


def get_allow_networking():
    if bpy.app.version >= (4, 2, 0):
        return bpy.app.online_access
    else:
        return True


def get_wm_props(source: Context = None) -> "WindowManagerProps":
    source = source if source else bpy.context
    return source.window_manager.gscatter


def get_scene_props(source: Union[Context, Depsgraph] = None) -> "SceneProps":
    source = source if source else bpy.context
    return source.scene.gscatter


def get_scatter_surface(
    source: Union[Context, Depsgraph] = None,
) -> Union[Object, None]:
    scene_props = get_scene_props(source)
    return scene_props.scatter_surface


def get_scatter_props(
    source: Union[Context, Depsgraph] = None,
) -> Union["ObjectProps", None]:
    scatter_surface = get_scatter_surface(source)
    return scatter_surface.gscatter if scatter_surface else None


def get_scatter_item(
    source: Union[Context, Depsgraph] = None,
) -> Union["ScatterItemProps", None]:
    scatter_props = get_scatter_props(source)
    if scatter_props and scatter_props.scatter_index in range(
        len(scatter_props.scatter_items)
    ):
        return scatter_props.scatter_items[scatter_props.scatter_index]


def get_scatter_system(source: Union[Context, Depsgraph] = None) -> Union[Object, None]:
    scatter_props = get_scatter_props(source)
    if scatter_props and scatter_props.scatter_index in range(
        len(scatter_props.scatter_items)
    ):
        return scatter_props.scatter_items[scatter_props.scatter_index].obj


def get_nodes_modifier(
    source: Union[Context, Depsgraph, Object] = None,
) -> Union[NodesModifier, None]:
    scatter_system = (
        source if isinstance(source, Object) else get_scatter_system(source)
    )
    if scatter_system:
        return scatter_system.modifiers.get("GScatterGeometryNodes")


def get_system_tree(
    source: Union[Context, Depsgraph, Object] = None,
) -> Union[bpy.types.GeometryNodeTree, None]:
    nodes_modifier = get_nodes_modifier(source)
    return nodes_modifier.node_group if nodes_modifier else None


def get_node_tree(
    source: Union[Context, Depsgraph, Object] = None,
) -> Union[GeometryNodeTree, None]:
    nodes_modifier = get_nodes_modifier(source)
    if nodes_modifier and nodes_modifier.node_group:
        node = nodes_modifier.node_group.nodes.get("GScatter")
        if node is None:
            node_tree = nodes_modifier.node_group
        else:
            node_tree = node.node_tree
        return node_tree
    return None


def get_system_effects_folder() -> str:
    base_path = join(dirname(pathlib.Path(__file__).parent.resolve()))
    return join(base_path, "effects", "data", "system")


def get_internal_effects_folder() -> str:
    base_path = join(dirname(pathlib.Path(__file__).parent.resolve()))
    return join(base_path, "effects", "data", "internal")


def get_instance_col(
    source: Union[Context, Depsgraph, Object] = None,
) -> Union[bpy.types.Collection, None]:
    node_tree = get_node_tree(source)
    if node_tree:
        node: bpy.types.GeometryNodeGroup = node_tree.nodes["GEOMETRY"]
        for effect in node.node_tree.gscatter.effects:
            effect_id = (
                effect.get_effect_id() if effect.get_effect_id() else effect.effect_id
            )
            if effect_id == "system.instance_collection":
                effect_node = node.node_tree.nodes[
                    effect.name + "_group"
                ].node_tree.nodes.get("effect")
                if effect_node is not None:
                    col = (
                        node.node_tree.nodes[effect.name + "_group"]
                        .node_tree.nodes["effect"]
                        .inputs["Collection"]
                        .default_value
                    )
                    return col
                else:
                    return (
                        node.node_tree.nodes[effect.name + "_group"]
                        .inputs["Collection"]
                        .default_value
                    )
    return None


def get_scatter_system_effects(item, is_old=False):
    distribution = []
    scale = []
    rotation = []
    geometry = []
    categories = ["DISTRIBUTION", "SCALE", "ROTATION", "GEOMETRY"]
    gscatter_assets = list()
    node_tree = get_node_tree(item)

    dependencies = {
        "objects": set(),
        "collections": set(),
        "images": set(),
        "materials": set(),
    }

    for category in categories:
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effect_list = node.node_tree.gscatter.effects
        for effect in effect_list:
            effect_data, dependency = get_effect_data(effect, is_old, gscatter_assets)

            dependencies["objects"].update(dependency[0])
            dependencies["collections"].update(dependency[1])
            dependencies["images"].update(dependency[2])
            dependencies["materials"].update(dependency[3])

            if category == "DISTRIBUTION":
                distribution.append(effect_data)
            elif category == "SCALE":
                scale.append(effect_data)
            elif category == "ROTATION":
                rotation.append(effect_data)
            else:
                geometry.append(effect_data)

    return distribution, scale, rotation, geometry, gscatter_assets, dependencies


def get_effect_data(
    effect,
    is_old,
    gscatter_assets,
):
    effect_id = effect.get_effect_id() if effect.get_effect_id() else effect.effect_id
    effect_version = (
        effect.get_effect_version() if effect.get_effect_version() else effect.version
    )
    instance_id = effect.instance_id if effect.instance_id else str(uuid4())
    if effect.instance_id == "":
        effect.instance_id = instance_id
    effect_data = {
        "name": effect.group_node.node_tree.name,
        "effect_id": effect_id,
        "effect_version": effect_version,
        "effect_instance_id": instance_id,
        "params": {},
        "layer_params": {},
        "nodes": {},
    }
    params = {}
    index = 0
    if effect.effect_node is None:
        return

    mats = set()
    objs = set()
    collections = set()
    images = set()

    for inp in effect.effect_node.inputs.values():
        if (
            len(inp.links) == 0
            and inp.bl_idname not in NON_PRIMITIVE_SOCKETS
            and not inp.name.startswith("_")
        ):
            idx = index + 1 if is_old else index
            if inp.type in ["OBJECT", "COLLECTION", "IMAGE", "MATERIAL"]:
                params[str(idx)] = {
                    "type": inp.type,
                    "name": inp.default_value.name if inp.default_value else None,
                }

                if (
                    inp.type == "OBJECT"
                    and inp.default_value
                    and not inp.default_value.gscatter.is_gscatter_system
                ):
                    objs.add(inp.default_value)
                elif inp.type == "IMAGE" and inp.default_value:
                    images.add(inp.default_value)
                elif inp.type == "MATERIAL" and inp.default_value:
                    mats.add(inp.default_value)

                elif inp.type == "COLLECTION":
                    params[str(idx)]["is_gscatter_asset"] = (
                        inp.default_value.gscatter.is_gscatter_asset
                        if inp.default_value
                        else False
                    )
                    if (
                        inp.default_value
                        and inp.default_value.gscatter.is_gscatter_asset
                    ):
                        asset_id = (
                            inp.default_value.gscatter.asset_id
                            if inp.default_value.gscatter.asset_id
                            else inp.default_value.name.split(":")[-1]
                        )

                        library = bpy.context.window_manager.gscatter.library
                        asset = [
                            ass for ass in library.assets if ass.asset_id == asset_id
                        ]

                        if asset:
                            params[str(idx)]["asset_id"] = asset_id

                            asset_name = asset[0].name.rsplit(" ", 1)[0]
                            # debug(asset_name)

                            ob = inp.default_value.name.split(":")[0]
                            # debug(ob)

                            ob_name_split = ob.removeprefix(asset_name + " ").split(" ")
                            # debug(ob_name_split)

                            params[str(idx)]["variant"] = ob_name_split[0]
                            params[str(idx)]["lod"] = ob_name_split[-1].removeprefix(
                                "LOD"
                            )

                            gscatter_assets.append(asset_id)

                    elif (
                        inp.default_value
                        and not inp.default_value.gscatter.is_gscatter_asset
                    ):
                        collections.add(inp.default_value)
            else:
                params[str(idx)] = clean(inp.default_value)

        index += 1
    dropdowns = {}
    for dropdown in effect.dropdowns:
        dropdowns[dropdown.name] = dropdown.dropdown_items
    if effect.mix_node:
        try:
            layer_params = {
                "blendmode": effect.mix_node.blend_type,
                "influence": effect.mix_node.inputs[0].default_value,
            }
        except Exception:
            layer_params = {
                "blendmode": effect.blend_type,
                "influence": effect.influence,
                "invert": effect.invert,
            }
    else:
        layer_params = None
    nodes = get_node_properties(effect.effect_node.node_tree, gscatter_assets)

    effect_data["params"] = params
    effect_data["layer_params"] = layer_params
    effect_data["nodes"] = nodes
    effect_data["dropdowns"] = dropdowns

    return effect_data, (objs, collections, images, mats)


def get_nodes_from_node_tree(node_tree: bpy.types.GeometryNodeTree, nodes: set):
    for node in node_tree.nodes:
        if node.type == "GROUP" and node.node_tree:
            get_nodes_from_node_tree(node.node_tree, nodes)
        elif node.gscatter.display_in_effect:
            nodes.add(node)


def get_node_properties(node_tree: bpy.types.GeometryNodeTree, gscatter_assets: list):
    """Returns a dict with the properties of all nodes in a nodetree"""
    node_data = {}

    # Get all the nodes
    nodes = set()
    get_nodes_from_node_tree(node_tree, nodes)

    for node in nodes:
        if not node.gscatter.display_in_effect:
            continue
        data = {}
        if hasattr(node, "color_ramp"):
            data["color_ramp"] = []
            for c in node.color_ramp.elements:
                data["color_ramp"].append((c.position, list(c.color)))
        elif node.type == "CURVE_FLOAT":
            data["curve_float"] = []
            for curve in node.mapping.curves:
                points = []
                for p in curve.points:
                    points.append((tuple(p.location), p.handle_type))
                data["curve_float"].append(points)
        elif node.type == "CURVE_RGB":
            data["curve_rgb"] = []
            for curve in node.mapping.curves:
                points = []
                for p in curve.points:
                    points.append((tuple(p.location), p.handle_type))
                data["curve_rgb"].append(points)

        data["props"] = {}
        internal_props = [
            "rna_type",
            "type",
            "location",
            "location_absolute",
            "width",
            "width_hidden",
            "height",
            "dimensions",
            "name",
            "label",
            "inputs",
            "outputs",
            "internal_links",
            "parent",
            "use_custom_color",
            "color",
            "color_tag",
            "select",
            "show_options",
            "show_preview",
            "hide",
            "mute",
            "show_texture",
            "bl_idname",
            "bl_label",
            "bl_description",
            "bl_icon",
            "bl_static_type",
            "bl_width_default",
            "bl_width_min",
            "bl_width_max",
            "bl_height_default",
            "bl_height_min",
            "bl_height_max",
            "texture_mapping",
            "color_mapping",
            "warning_propagation",
        ]
        for p in node.bl_rna.properties:
            if p.identifier not in internal_props and p.type not in [
                "POINTER",
                "COLLECTION",
            ]:
                data["props"].update({p.identifier: getattr(node, p.identifier)})
        if hasattr(node, "color_ramp"):
            data["color_ramp_props"] = {
                "color_mode": node.color_ramp.color_mode,
                "interpolation": node.color_ramp.interpolation,
                "hue_interpolation": node.color_ramp.hue_interpolation,
            }

        data["params"] = get_params(node, gscatter_assets=gscatter_assets)
        node_data.update({node.name: data})
    return node_data


def get_materials_in_system(item) -> set[bpy.types.Material]:
    materials = set()
    node_tree = get_node_tree(item)
    category = "GEOMETRY"
    node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
    effect_list = node.node_tree.gscatter.effects
    for effect in effect_list:
        if effect.effect_node is None:
            continue
        for inp in effect.effect_node.inputs.values():
            if len(inp.links) == 0 and inp.type == "MATERIAL":
                if inp.type == "MATERIAL" and inp.default_value:
                    materials.add(inp.default_value)

    return materials


def get_params(node, gscatter_assets) -> dict:
    params = {}
    for idx, inp in enumerate(node.inputs.values()):
        if (
            len(inp.links) == 0
            and inp.bl_idname not in NON_PRIMITIVE_SOCKETS
            and not inp.name.startswith("_")
        ):
            if inp.type in ["OBJECT", "COLLECTION", "IMAGE", "MATERIAL"]:
                params[str(idx)] = {
                    "type": inp.type,
                    "name": inp.default_value.name if inp.default_value else None,
                }
                if inp.type == "COLLECTION":
                    params[str(idx)]["is_gscatter_asset"] = (
                        inp.default_value.gscatter.is_gscatter_asset
                        if inp.default_value
                        else False
                    )
                    if (
                        inp.default_value
                        and inp.default_value.gscatter.is_gscatter_asset
                    ):
                        asset_id = (
                            inp.default_value.gscatter.asset_id
                            if inp.default_value.gscatter.asset_id
                            else inp.default_value.name.split(":")[-1]
                        )

                        params[str(idx)]["asset_id"] = asset_id

                        ob = inp.default_value.name.split(":")[0]
                        ob_name_split = ob.split(" ")

                        params[str(idx)]["variant"] = ob_name_split[-2]
                        params[str(idx)]["lod"] = ob_name_split[-1].removeprefix("LOD")

                        gscatter_assets.append(asset_id)
            else:
                params[str(idx)] = clean(inp.default_value)
    return params


def get_user_library(context: bpy.types.Context):
    prefs = get_preferences(context)
    library = pathlib.Path(prefs.t3dn_library)
    library.mkdir(exist_ok=True, parents=True)
    return library


def get_user_assets_dir(context: bpy.types.Context):
    prefs = get_preferences(context)
    library = pathlib.Path(prefs.t3dn_library)
    assets_dir = library.joinpath("Assets")
    assets_dir.mkdir(exist_ok=True, parents=True)
    return assets_dir


def get_asset_browser_dir(context: bpy.types.Context = None):
    prefs = get_preferences(context)
    library = pathlib.Path(prefs.t3dn_library)
    asset_browser_dir = library.joinpath("AssetBrowser")
    asset_browser_dir.mkdir(exist_ok=True, parents=True)
    return asset_browser_dir
