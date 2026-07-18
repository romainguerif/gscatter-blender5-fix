import bpy
from bpy.types import Context
from typing import TYPE_CHECKING
from ..common.ui import BasePanel
from ..utils.getters import (
    get_allow_networking,
    get_scatter_props,
    get_scene_props,
)  # , get_preferences
from .ops import (
    AddNewEnvironmentPropertyOperator,
    CreateEnvironmentOperator,
    PreviewOperator,
    PropertyInfo,
    ReorderPropertyOperator,
    RenameProperty,
    RemovePropertyOperator,
)
from ..asset_manager.previews import get
from .utils import get_effect

# if TYPE_CHECKING:
#     from ..effects.props import EffectLayerProps
if TYPE_CHECKING:
    from ..asset_manager.props.library import LibraryWidget
    from ..asset_manager.props.free_assets import FreeAssetWidget


class EnvironmentCreatorPanel(BasePanel):
    bl_idname = "GSCATTER_PT_EnvironmentPanel"
    bl_label = "Environment Creator"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2
    bl_parent_id: str = "GSCATTER_PT_scatter"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        scene_props = get_scene_props(context)
        scatter_props = get_scatter_props(context)
        return scene_props.scatter_surface and scatter_props.scatter_items

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(icon="WORLD")  # icon="PACKAGE")

    def draw(self, context: bpy.types.Context):
        scene_props = get_scene_props(context)
        environment_creator = scene_props.environment_creator
        layout = self.layout

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(environment_creator, "name")
        col.prop(environment_creator, "description")
        col.prop(environment_creator, "author")
        col.prop(environment_creator, "terrain_material")
        col = col.column(align=True)
        # col.prop(environment_creator, "preview", text="Thumbnail")
        row = col.row(align=True)
        row.prop(environment_creator, "preview")
        row.operator(PreviewOperator.bl_idname, text="", icon="FILE_IMAGE")

        if environment_creator.preview:
            col.box().template_icon(
                icon_value=get(environment_creator.preview).icon_id, scale=10
            )

        col = layout.box().column(align=True)
        row = col.row()
        row.alignment = "LEFT"
        row.prop(
            environment_creator,
            "show_systems",
            text="Select systems for environment",
            toggle=True,
            icon="TRIA_RIGHT" if not environment_creator.show_systems else "TRIA_DOWN",
            emboss=False,
        )
        if environment_creator.show_systems:
            scatter_surface = scene_props.scatter_surface
            col = col.box().column()
            for item in scatter_surface.gscatter.scatter_items:
                col.prop(item, "environment_selection", text=item.obj.name)

        col = layout.column()
        col.scale_y = 1.2
        col.operator(CreateEnvironmentOperator.bl_idname, icon="PACKAGE")


class EnvironmentPropsPanel(BasePanel):
    bl_idname = "GSCATTER_PT_EnvironmentProps"
    bl_label = "Environment Properties"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 0
    bl_parent_id: str = "GSCATTER_PT_scatter"

    @classmethod
    def poll(cls, context):
        scene_props = get_scene_props(context)
        scatter_props = get_scatter_props(context)
        return scene_props.scatter_surface and scatter_props.scatter_items

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(icon="WORLD")

    def draw_header_preset(self, context: Context):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface

        layout = self.layout.row(align=True)
        layout.operator(AddNewEnvironmentPropertyOperator.bl_idname, text="Add")
        layout.prop(
            ss.gscatter.environment_props,
            "editing",
            text="",
            icon="GREASEPENCIL",
            toggle=True,
        )

    def draw(self, context):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface

        layout = self.layout
        # layout.use_property_split = True
        layout.use_property_decorate = not ss.gscatter.environment_props.editing

        env_props = ss.gscatter.environment_props.props

        props = [(idx, prop) for idx, prop in enumerate(env_props)]
        props.sort(key=lambda x: x[1].order_idx)

        if len(props) == 0:
            layout.enabled = False
            row = layout.row()
            row.alignment = "CENTER"
            row.label(text="You have not added any properties yet.", icon="QUESTION")

        for prop in props:
            idx = prop[0]
            prop = prop[1]
            effect = get_effect(context, ss, prop.effect_instance_id)
            if effect is None:
                continue
            try:
                input = effect.effect_node.inputs[prop.input_idx]
            except Exception:
                continue
            split = layout.split(
                factor=0.8 if ss.gscatter.environment_props.editing else 1, align=True
            )
            # split.prop(input, "default_value", text=prop.label)
            row0 = split.row(align=True)
            op = row0.operator(PropertyInfo.bl_idname, text=prop.label, emboss=False)
            op.tooltip = f"{input.name} \n\u2022 {effect.group_node.node_tree.name}"
            # row0 = row0.prop(input, "default_value", text="", emboss=False)
            row0 = input.draw(context, row0, effect.effect_node, "")
            if ss.gscatter.environment_props.editing:
                row = split.row(align=True)
                row.alignment = "RIGHT"
                row.separator(factor=0.3)
                op = row.operator(
                    ReorderPropertyOperator.bl_idname, text="", icon="TRIA_UP"
                )
                op.prop_idx = idx
                op.direction = "UP"
                op.tooltip = "UP"
                op = row.operator(
                    ReorderPropertyOperator.bl_idname, text="", icon="TRIA_DOWN"
                )
                op.prop_idx = idx
                op.direction = "DOWN"
                op.tooltip = "DOWN"
                op = row.operator(
                    RenameProperty.bl_idname, text="", icon="GREASEPENCIL"
                )
                op.prop_idx = idx
                row.separator(factor=0.3)
                op = row.operator(
                    RemovePropertyOperator.bl_idname, text="", icon="X", emboss=False
                )
                op.prop_idx = idx


class DownloadFreeAssetsPanel(BasePanel):
    bl_idname = "GSCATTER_PT_DownloadFreeAssets"
    bl_label = "Download Free Assets"
    bl_order = 120
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        # prefs = get_preferences()

        if not get_allow_networking():
            return False

        library = context.window_manager.gscatter.library
        if library.loading_free_assets:
            return True

        for free_asset in library.free_assets:
            if free_asset.asset_type == "3D_PLANT" and library.get_asset(
                free_asset.asset_id
            ):
                continue
            elif (
                free_asset.asset_type == "ENVIRONMENT"
                and library.get_environment_by_id(free_asset.asset_id)
            ):
                continue
            elif (
                free_asset.asset_type == "ENVIRONMENT"
                and library.get_environment_by_name(free_asset.name)
            ):
                continue
            else:
                return True
        return False

    def draw_header(self, context: Context):
        self.layout.label(icon="IMPORT")

    def draw_header_preset(self, context: Context):
        layout = self.layout
        library = context.window_manager.gscatter.library
        if library.loading_free_assets:
            layout.label(text="Loading Assets", icon="INFO")
        else:
            op = layout.operator(
                "gscatter.refresh_library", text="", icon="FILE_REFRESH", emboss=False
            )
            op.load_free_assets = True
            op.tooltip = "Refresh list of available Free Assets to download. \n\u2022 Click to refresh free assets"

    def draw(self, context):
        context.area.tag_redraw()
        layout = self.layout
        col = layout.column(align=True)
        library: "LibraryWidget" = context.window_manager.gscatter.library
        environments: list["FreeAssetWidget"] = [
            asset for asset in library.free_assets if asset.asset_type == "ENVIRONMENT"
        ]
        assets: list["FreeAssetWidget"] = [
            asset for asset in library.free_assets if asset.asset_type == "3D_PLANT"
        ]

        for free_asset in environments + assets:
            free_asset.draw_compact(col)


classes = (
    EnvironmentPropsPanel,
    EnvironmentCreatorPanel,
    DownloadFreeAssetsPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
