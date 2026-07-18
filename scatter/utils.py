import itertools
from pathlib import Path

import bpy

from ..utils.getters import get_preferences


def get_available_systems(self, context):
    objs = [
        obj for obj in bpy.context.view_layer.objects if obj.gscatter.is_gscatter_system
    ]

    items = []
    indices = itertools.count()
    for obj in objs:
        items.append((obj.name, obj.name, "", "OUTLINER_COLLECTION", next(indices)))
    return items


def get_selected_asset(
    asser_browser_area: bpy.types.Area,
) -> list[bpy.types.Collection]:
    prefs = get_preferences()
    with bpy.context.temp_override(area=asser_browser_area):
        context = bpy.context
        current_library_name = ""

        try:
            current_library_name = context.area.spaces.active.params.asset_library_ref
        except AttributeError:
            current_library_name = (
                context.area.spaces.active.params.asset_library_reference
            )

        objs: list[bpy.types.Object] = []
        collections: list[bpy.types.Collection] = []

        selection = []
        try:
            if context.selected_asset_files:
                selection = context.selected_asset_files
        except AttributeError:
            if context.selected_assets:
                selection = context.selected_assets

        for asset_file in selection:
            if current_library_name == "LOCAL":
                if asset_file.id_type == "OBJECT":
                    objs.append(asset_file.local_id)
                elif asset_file.id_type == "COLLECTION":
                    collections.append(asset_file.local_id.copy())
            else:
                blend_path = Path(context.window_manager.asset_path_dummy)

                if not blend_path.exists():
                    if asset_file.id_type == "OBJECT":
                        objs.append(asset_file.local_id)
                    elif asset_file.id_type == "COLLECTION":
                        collections.append(asset_file.local_id.copy())
                else:
                    if asset_file.id_type == "OBJECT":
                        with bpy.data.libraries.load(
                            blend_path.as_posix(),
                            link=prefs.asset_import_mode == "LINK",
                        ) as (data_from, data_to):
                            data_to.objects.append(asset_file.name)
                        objs.append(data_to.objects[0])
                    elif asset_file.id_type == "COLLECTION":
                        with bpy.data.libraries.load(
                            blend_path.as_posix(),
                            link=prefs.asset_import_mode == "LINK",
                        ) as (data_from, data_to):
                            data_to.collections.append(asset_file.name)
                        collections.append(data_to.collections[0])

        if len(objs) > 0:
            new_col = bpy.data.collections.new(objs[0].name)
            for obj in objs:
                new_col.objects.link(obj)
            collections.append(new_col)
        return collections


def get_asset_browser(context):
    asset_areas = [area for area in context.screen.areas if area.ui_type == "ASSETS"]
    if asset_areas:
        return asset_areas[0]


def draw_terrain_selector(col, starter_props):
    terrain_col = col.box().column()
    terrain_col.label(text="Select Terrain type")
    row = terrain_col.row()
    row.prop(starter_props, "terrain_type", expand=True)
    row = terrain_col.row()
    row.enabled = False
    if starter_props.terrain_type == "DEFAULT":
        row.label(text="Use terrain from selected environment.")
    elif starter_props.terrain_type == "NEW":
        row.label(text="Generate a new terrain.")
        terrain_col.prop(
            starter_props,
            "use_terrain_material",
            text="Use Default Environment Terrain Material",
        )
    else:
        row.label(text="Select your own terrain.")
        terrain_col.prop(starter_props, "custom_terrain")
        terrain_col.prop(
            starter_props,
            "use_terrain_material",
            text="Use Default Environment Terrain Material",
        )
