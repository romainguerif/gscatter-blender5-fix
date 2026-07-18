from typing import TYPE_CHECKING, List

import bpy
from bpy.types import Context

from .. import icons
from ..asset_manager.ops.popup import AssetBrowserPopup, GraswaldAssetLibraryPopup
from ..common.props import ScatterItemProps, SceneProps
from ..common.ui import BasePanel
from ..effects.props import EffectLayerProps
from ..scatter.utils import get_available_systems
from ..utils.getters import (
    get_node_tree,
    get_preferences,
    get_scatter_props,
    get_scene_props,
    get_system_tree,
    get_version,
    get_wm_props,
)
from . import default
from .ops import (
    SetSystemListOperator,
    MakeUniqueSystemOperator,
    UpdateScatterSystemTreeOperator,
    ToggleProxyOperator,
    ToggleVisibilityOperator,
    ScatterSelectedToActive,
    CreateLinkedSystemOperator,
    ScatterOperator,
    DeleteScatterItemOperator,
    DuplicateScatterItemOperator,
    MoveScatterItemOperator,
    AddNewSystemPresetOperator,
    ChangePresetOperator,
    RemovePresetOperator,
    CreateEnvionmentFromTemplateOperator,
)
from .store import scattersystempresetstore
from .utils import draw_terrain_selector

if TYPE_CHECKING:
    from ..asset_manager.props.library import LibraryWidget


def get_geometry_effect_types(obj: bpy.types.Object) -> List[EffectLayerProps]:
    try:
        node_tree = get_node_tree(obj)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes["GEOMETRY"]
        effects: List[EffectLayerProps] = node.node_tree.gscatter.effects
        return [effect.get_effect_id() for effect in effects]
    except Exception:
        return []


class ScatterItemList(bpy.types.UIList):
    bl_idname = "GSCATTER_UL_scatter_item"

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item: ScatterItemProps,
        icon,
        active_data,
        active_propname,
        index,
    ):
        obj: bpy.types.Object = item.obj
        effect_types = get_geometry_effect_types(obj)

        main_tree = get_system_tree(obj)
        node_tree = get_node_tree(obj)

        # System Type Icon Display
        show_icon = True
        if ("system.instance_object" in effect_types) and (
            "system.instance_collection" not in effect_types
        ):
            icon = "MESH_CUBE"
        elif ("system.instance_object" not in effect_types) and (
            "system.instance_collection" in effect_types
        ):
            icon = "OUTLINER_COLLECTION"
        elif ("system.instance_object" in effect_types) and (
            "system.instance_collection" in effect_types
        ):
            icon = "STICKY_UVS_DISABLE"
        elif "e623fc66b5c243f189bc6276e80f0fe7" in effect_types:
            icon = "WORLD"
        else:
            show_icon = False
            icon = "ERROR"

        # Begin Layout
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            #
            ## LEFT
            #
            row = layout.row(align=True)

            # Update ScatterSystem if detected
            if item.get_ntree_version() != default.NODETREE_VERSION:
                op = row.operator(
                    UpdateScatterSystemTreeOperator.bl_idname,
                    text="",
                    icon="ERROR",
                    emboss=False,
                )
                op.mode = "SINGLE"
                op.system_index = index

            # Layout System Color picker
            sub_row = row.row()
            sub_row.scale_x = 0.3
            sub_row.prop(item, "color", text="", icon_only=True)

            # Layout Systems dropwdown & Make Unique Button
            sub_row = row.row(
                align=True
            )  # parent element for both dropwdown and user count
            rr = sub_row.row(align=True)
            rr.scale_x = 1.3
            op = rr.operator_menu_enum(
                SetSystemListOperator.bl_idname,
                "type",
                icon="OUTLINER_OB_POINTCLOUD",
                text="",
            )
            op.index = index

            # Layout Make Unique Button if multiple instnaces of the same systme exist
            if effect_types != []:
                users = len(main_tree.nodes["Join Geometry"].inputs[0].links)
                if users > 1:
                    rr = sub_row.row(align=True)
                    rr.scale_x = 0.7
                    rr.alignment = "LEFT"
                    op = rr.operator(
                        MakeUniqueSystemOperator.bl_idname, text=str(users)
                    )
                    op.group_name = node_tree.name
                    op.index = index

            #
            ## System name
            #
            # Layout System name
            row = sub_row.row(align=True)
            if show_icon:
                sub_row.label(text="", icon=icon)
            sub_row.prop(item.obj, "name", text="", emboss=False)

            #
            ## RIGHT
            #
            row = layout.row(align=True)
            row.alignment = "RIGHT"

            # Layout Instance counter # TODO perrformance issues getting istnace count of on object.
            # depsgraph = bpy.context.evaluated_depsgraph_get()
            # eval_obj = obj.evaluated_get(depsgraph)
            # instances = sum(1 for inst in depsgraph.object_instances if inst.is_instance and inst.parent == eval_obj)
            # # instances = eval_obj.
            # print(instances)

            # large_number = instances
            # abbreviations = [(1e12, 'T'), (1e9, 'B'), (1e6, 'M'), (1e3, 'k'), (1, '')]

            # instance_display = "0"
            # for factor, suffix in reversed(abbreviations):
            #     if large_number >= factor:
            #         instance_display = f"{round(large_number / factor)}{suffix}"

            # row.label(text="", icon="EMPTY_AXIS")
            # row.label(text=instance_display)

            # Layout toggle proxy button

            op: ToggleProxyOperator = row.operator(
                ToggleProxyOperator.bl_idname,
                text="",
                icon_value=icons.get("proxy_inactive")
                if not item.viewport_proxy
                else icons.get("proxy_active"),
                emboss=False,
            )
            op.all_except_current = op.all = False
            op.index = index

            # row.prop(
            #     item,
            #     "viewport_proxy",
            #     icon_only=True,
            #     icon_value=icons.get('proxy_inactive') if not item.viewport_proxy else icons.get('proxy_active'),
            #     emboss=False,
            #     toggle=True,
            # )

            # Layout toggle viewport visibility
            op: ToggleVisibilityOperator = row.operator(
                ToggleVisibilityOperator.bl_idname,
                text="",
                icon="HIDE_OFF" if obj.visible_get() else "HIDE_ON",
                emboss=False,
            )
            op.all_except_current = op.all = False
            op.index = index

            # Layout toggle disable in render
            row.prop(obj, "hide_render", text="", emboss=False)
            row.separator(factor=0.5)

    def filter_items(self, context, data, propname):
        scatter_items = getattr(data, propname)
        objs = [item.obj for item in scatter_items]

        helper_funcs = bpy.types.UI_UL_list

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # Filtering by name
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(
                self.filter_name, self.bitflag_filter_item, objs, "name", reverse=False
            )

        # Reorder by alphabet
        if self.use_filter_sort_alpha:
            flt_neworder = helper_funcs.sort_items_by_name(objs, "name")

        return flt_flags, flt_neworder


class EmptyScatterItemList(
    bpy.types.UIList
):  # For showing help message instead of an actually empty lsit
    bl_idname = "GSCATTER_UL_empty_scatter_item"

    # Called for each drawn item.
    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
        flt_flag,
    ):
        # 'DEFAULT' and 'COMPACT' layout types should usually use the same draw code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.enabled = False
            row = layout.row()
            row.alignment = "CENTER"
            col = row.column()
            col.scale_y = 0.93
            row = col.row()
            row.alignment = "CENTER"
            row.label(text="No Scatter System(s) to display.", icon="QUESTION")
            row = col.row()
            row.label(text="")
            row = col.row()
            row.alignment = "CENTER"
            row.label(text="To create a System, select objects")
            row = col.row()
            row.alignment = "CENTER"
            row.label(text="or assets and click '+ Scatter selected'.")
            row = col.row(align=True)
            row.alignment = "CENTER"
            row.label(text="Or click the library icon")
            row.label(text="to open the ", icon="ASSET_MANAGER")
            row = col.row()
            row.alignment = "CENTER"
            row.label(text="AssetBrowser to access Graswald Assets.")
            row = col.row()
            row.alignment = "CENTER"
            row.label(text="Download your first free assets below!", icon="IMPORT")
            row = col.row()
            row.label(text="")
            row.scale_y = 1.1
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {"GRID"}:
            pass

    # Called once to filter/reorder items.
    def filter_items(self, context, data, propname):
        flt_flags = []
        flt_neworder = []
        return flt_flags, flt_neworder


def draw_emitter(
    context: bpy.types.Context, layout: bpy.types.UILayout, scene_props: SceneProps
):
    # Layout emitter object dropdown input
    box = layout.box()
    row = box.row(align=True)
    row.scale_y = 1.2
    sub_row = row.row(align=True)
    sub_row.label(text="", icon="SCENE_DATA")
    sub_row.alignment = "RIGHT"
    sub_row.label(text="Emitter")

    # Use active object as scatter surface
    row.separator()
    sub_row = row.row(align=True)
    sub_row.alignment = "RIGHT"
    # icon = "DECORATE_LOCKED" if scene_props.use_active_object_as_scatter_surface else "DECORATE_UNLOCKED"
    icon = (
        "RESTRICT_SELECT_OFF"
        if scene_props.use_active_object_as_scatter_surface
        else "RESTRICT_SELECT_ON"
    )
    sub_row.prop(
        scene_props,
        "use_active_object_as_scatter_surface",
        toggle=True,
        icon=icon,
        text="",
    )

    row.separator()
    sub_row = row.row(align=True)
    sub_row.prop_search(
        scene_props, "scatter_surface", context.view_layer, "objects", text=""
    )
    sub_row.enabled = not scene_props.use_active_object_as_scatter_surface

    return box


class ScatterPanel(BasePanel):
    bl_idname = "GSCATTER_PT_scatter"
    bl_label = "GScatter"

    # bl_order = 100

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        scene_props = get_scene_props(context)
        return scene_props.scatter_surface is not None

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(icon_value=icons.get("graswald"))

    def draw_header_preset(self, context: Context):
        layout = self.layout
        layout.label(text="v" + ".".join(map(str, get_version())))

    def draw(self, context: bpy.types.Context):
        scene_props = get_scene_props(context)
        prefs = get_preferences(context)
        layout = self.layout.column(align=True)
        draw_emitter(context, layout, scene_props)
        if scene_props.scatter_surface is not None:
            box = layout.box()
            scatter = get_scatter_props(context)

            row = box.row()
            sub_row = row.row(align=True)
            rr = sub_row.row(align=True)
            rr.scale_x = 1.3
            rr.enabled = len(get_available_systems(self, context)) > 0
            rr.operator_menu_enum(
                CreateLinkedSystemOperator.bl_idname,
                "type",
                text="",
                icon="OUTLINER_OB_POINTCLOUD",
            )
            sub_row.operator(
                ScatterOperator.bl_idname, text="Scatter selected", icon="ADD"
            ).individual = False
            sub_row.operator(
                DeleteScatterItemOperator.bl_idname, text="", icon="REMOVE"
            )

            if prefs.enable_experimental_features:
                row.operator(
                    GraswaldAssetLibraryPopup.bl_idname, text="", icon="ASSET_MANAGER"
                )
            else:
                row.operator(AssetBrowserPopup.bl_idname, text="", icon="ASSET_MANAGER")

            row.popover(ScatterSystemPresetPanel.bl_idname, text="", icon="PRESET")
            row.operator(
                DuplicateScatterItemOperator.bl_idname, text="", icon="DUPLICATE"
            )
            rr = row.row(align=True)
            rr.operator(
                MoveScatterItemOperator.bl_idname, text="", icon="TRIA_UP"
            ).direction = "UP"
            rr.operator(
                MoveScatterItemOperator.bl_idname, text="", icon="TRIA_DOWN"
            ).direction = "DOWN"

            row = box.row()
            col = row.column(align=True)
            col.scale_y = 0.95
            wm_props = get_wm_props(context)
            if len(scatter.scatter_items) < 1:
                col.template_list(
                    EmptyScatterItemList.bl_idname,
                    "",
                    wm_props,
                    "empty_list",
                    wm_props,
                    "empty_index",
                    rows=1,
                )
            else:
                col.template_list(
                    ScatterItemList.bl_idname,
                    "",
                    scatter,
                    "scatter_items",
                    scatter,
                    "scatter_index",
                    rows=8,
                )
            """col = row.column(align=True)
            col.scale_y = col.scale_x = 1.05
            col.popover(ScatterSystemPresetPanel.bl_idname, text="", icon="PRESET")
            col.separator()
            col.operator(DuplicateScatterItemOperator.bl_idname, text='', icon='DUPLICATE')
            col.separator()
            col.operator(MoveScatterItemOperator.bl_idname, text='', icon='TRIA_UP').direction = 'UP'
            col.operator(MoveScatterItemOperator.bl_idname, text='', icon='TRIA_DOWN').direction = 'DOWN'"""


class ScatterSystemPresetPanel(bpy.types.Panel):
    bl_idname = "GSCATTER_PT_scatter_system_presets"
    bl_label = "Scatter System Presets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    # @classmethod
    # def poll(cls, context):
    #     scatter_props = get_scatter_props(context)
    #     items: list[ScatterItemProps] = scatter_props.scatter_items
    #     index: int = scatter_props.scatter_index
    #     return index in range(len(items))

    def draw(self, context):
        layout = self.layout
        wm_props = get_wm_props(context)
        row = layout.row()
        row.prop(wm_props, "new_preset", text="")
        row.operator(
            AddNewSystemPresetOperator.bl_idname, text="", icon="ADD", emboss=False
        )

        for preset in scattersystempresetstore.get_all():
            row = layout.row()
            row.operator(
                ChangePresetOperator.bl_idname, text=preset.name, emboss=False
            ).type = preset.id
            sub = row.row()
            sub.enabled = not preset.id.startswith("system.")
            sub.operator(
                RemovePresetOperator.bl_idname, text="", icon="REMOVE", emboss=False
            ).type = preset.id


class GscatterStartPanel(BasePanel):
    bl_idname = "GSCATTER_PT_start"
    bl_label = "GScatter"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        scene_props = get_scene_props(context)
        return scene_props.scatter_surface is None

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(icon_value=icons.get("graswald"))

    def draw_header_preset(self, context: Context):
        layout = self.layout
        layout.label(text="v" + ".".join(map(str, get_version())))

    def draw_environment_template_view(self, layout, context):
        wm_props = get_wm_props(context)
        starter_props = wm_props.scatter_starter
        library: "LibraryWidget" = context.window_manager.gscatter.library
        # layout = self.layout

        col = layout.column(align=True)
        env = library.get_environment_by_id(library.environment_enums)
        if env:
            env_detail_col = col.box().column()
            env.draw_template(env_detail_col, context.region.width - 50)
            env.draw_environment_setup(col)

        col.separator()
        draw_terrain_selector(col, starter_props)

        col.separator()
        create_row = col.row(align=True)
        create_row.scale_y = 1.5
        create_row.operator(
            CreateEnvionmentFromTemplateOperator.bl_idname, text="Create Environment"
        )

    def draw(self, context):
        scene_props = get_scene_props(context)
        wm_props = get_wm_props(context)
        prefs = get_preferences()
        library: "LibraryWidget" = context.window_manager.gscatter.library
        layout = self.layout

        # Layout emitter object dropdown input
        draw_emitter(context, layout, scene_props)

        # Scatter Selected to Active
        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 1.2
        sub_row = row.row(align=True)
        sub_row.label(text="", icon="STICKY_UVS_DISABLE")
        sub_row.label(text="", icon="FORWARD")
        sub_row.label(text="", icon="GRID")
        row.separator()
        row.separator()
        sub_row = row.row(align=True)
        context.copy()
        with context.temp_override(selected_to_active=True):
            op = sub_row.operator(
                ScatterSelectedToActive.bl_idname, text="Selected to Active"
            )

        # Environment Section
        col = layout.column(align=True)
        box = col.box()
        row = box.row()  # (align=True)
        row.scale_y = 1.2
        title = row.row(align=True)
        title.alignment = "LEFT"
        title.prop(
            wm_props,
            "show_environment_presets_list",
            text="",
            icon="WORLD",
            emboss=False,
        )
        title.prop(
            wm_props,
            "show_environment_presets_list",
            text="Environments",
            icon="TRIA_RIGHT"
            if not wm_props.show_environment_presets_list
            else "TRIA_DOWN",
            emboss=False,
        )

        # blank = row.row(align=True)
        # blank.prop(wm_props, "show_environment_presets_list", text=" ", icon="BLANK1", emboss=False)

        blank = row.row(align=True)
        blank.alignment = "RIGHT"
        if prefs.enable_experimental_features:
            blank.operator(
                GraswaldAssetLibraryPopup.bl_idname, text="", icon="ASSET_MANAGER"
            )
        else:
            blank.operator(AssetBrowserPopup.bl_idname, text="", icon="ASSET_MANAGER")

        if not wm_props.show_environment_presets_list:
            return

        box = col.box()
        if len(library.environments) == 0:
            col = box.column(align=True)
            col.enabled = False
            col.scale_y = 0.8
            col.scale_x = 1.0
            line = col.row()
            line.alignment = "CENTER"
            line.label(text="You don't have any", icon="QUESTION")
            line = col.row()
            line.alignment = "CENTER"
            line.label(text="environment installed yet.")
            line = col.row()
            line.alignment = "CENTER"
            line.label(text="Download a free one below.")
            # if prefs.enable_experimental_features:
            #     col.operator(DownloadFreeEnvironmentOperator.bl_idname, text="Download Free Environment.")

        else:
            row = box.row()
            left = row.column(align=True)
            center = row.column()
            right = row.column(align=True)

            left.scale_y = right.scale_y = 7
            left.scale_x = right.scale_x = 0.5
            left.active = right.active = False

            op = left.operator(
                "gscatter.scroll_environments", text="", icon="TRIA_LEFT", emboss=False
            )
            op.environment = library.environment_enums
            op.direction = -1
            center.template_icon_view(
                library, "environment_enums", show_labels=True, scale=8
            )
            op = right.operator(
                "gscatter.scroll_environments", text="", icon="TRIA_RIGHT", emboss=False
            )
            op.environment = library.environment_enums
            op.direction = 1

            if library.environment_enums != "SELECT_TEMPLATE":
                self.draw_environment_template_view(box, context)


classes = (
    ScatterSystemPresetPanel,
    ScatterItemList,
    EmptyScatterItemList,
    GscatterStartPanel,
    ScatterPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
