import bpy

from ...common.props import ProxySettingsProps
from ...utils.getters import (
    get_preferences,
    get_scatter_props,
    get_scene_props,
    get_wm_props,
)
from ...common.ui import BasePanel


class OptimizationPanel(BasePanel):
    bl_idname = "GSCATTER_PT_optimization"
    bl_label = "Optimization"
    bl_order = 2
    bl_options = {"DEFAULT_CLOSED"}
    # bl_parent_id: str = "GSCATTER_PT_scatter"

    @classmethod
    def poll(cls, context):
        scatter_props = get_scatter_props(context)
        return True and scatter_props  # and len(scatter_props.scatter_items) > 0

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(icon="MOD_REMESH")

    def draw(self, context):
        gscatter = get_scene_props(context)
        layout = self.layout
        col = layout.column()
        col.use_property_split = True
        col.prop(gscatter, "viewport_display_percentage", slider=True)


class CameraCullingPanel(BasePanel):
    bl_idname = "GSCATTER_PT_camera_culling"
    bl_label = "Camera Culling"
    bl_order = 112
    bl_parent_id: str = "GSCATTER_PT_optimization"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context: bpy.types.Context):
        gscatter = get_scene_props(context)
        layout = self.layout
        layout.prop(gscatter.camera_culling, "use", text="")

    def draw(self, context):
        scene_props = get_scene_props(context)
        camera_culling = scene_props.camera_culling
        wm_props = get_wm_props(context)
        show_exclude_list = wm_props.show_camera_culling_exluce_list

        layout = self.layout
        layout.enabled = camera_culling.use

        # Camera culling exlude systems list
        col = layout.box().column(align=True)
        row = col.row()
        row.prop(
            wm_props,
            "show_camera_culling_exluce_list",
            text="Select systems for camera culling",
            toggle=True,
            icon="TRIA_RIGHT" if not show_exclude_list else "TRIA_DOWN",
            emboss=False,
        )
        if show_exclude_list:
            scatter_props = get_scatter_props(context)
            if scatter_props:
                col = col.box().column()
                for item in scatter_props.scatter_items:
                    col.prop(item, "camera_culling", text=item.obj.name)

        # Layout Camera Culling Properties
        layout.use_property_split = True
        cam_col = layout.column()
        cam_col.prop(camera_culling, "use_active_camera")
        cam_seletor_col = cam_col.column()
        if camera_culling.use_active_camera:
            cam_seletor_col.enabled = False
        cam_seletor_col.prop_search(
            camera_culling, "camera", bpy.context.scene, "objects"
        )
        layout.prop(camera_culling, "focal_length")
        layout.prop(camera_culling, "sensor_size")
        layout.prop(camera_culling, "render_width")
        layout.prop(camera_culling, "render_height")
        layout.prop(camera_culling, "buffer")
        layout.prop(camera_culling, "backface_culling")
        layout.prop(camera_culling, "backface_threshold")
        layout.prop(camera_culling, "distance_culling")
        layout.prop(camera_culling, "distance_threshold")


class ProxySettingsPanel(BasePanel):
    bl_idname = "GSCATTER_PT_proxy_settings"
    bl_label = "Proxy Settings"
    bl_order = 113
    bl_parent_id: str = "GSCATTER_PT_optimization"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context: bpy.types.Context):
        get_scene_props(context)
        layout = self.layout
        # layout.prop(gscatter.proxy_settings, "proxy_method", text="")
        layout.separator()

    def draw(self, context):
        prefs = get_preferences(context)
        gscatter = get_scene_props(context)
        proxy_settings: ProxySettingsProps = gscatter.proxy_settings

        layout = self.layout
        layout.use_property_split = True
        layout.prop(prefs, property="use_proxy_on_new_systems")
        layout.prop(proxy_settings, "proxy_method")
        col = layout.column()
        row = col.row()
        row.prop(proxy_settings, "pc_density")
        row = col.row()
        row.prop(proxy_settings, "pc_size")
        if proxy_settings.proxy_method == proxy_settings.POINT_CLOUD:
            col.enabled = True
        else:
            col.enabled = False


class GlobalSettingsPanel(BasePanel):
    bl_idname = "GSCATTER_PT_global_settings"
    bl_label = "Preferences"
    bl_order = 114
    bl_parent_id: str = "GSCATTER_PT_optimization"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(icon="PREFERENCES")

    def draw(self, context):
        prefs = get_preferences(context)

        layout = self.layout
        box = layout.box()
        box.use_property_split = True
        box.prop(prefs, "default_scatter_preset")
        box.prop(prefs, "asset_import_mode")


classes = (
    OptimizationPanel,
    CameraCullingPanel,
    ProxySettingsPanel,
    GlobalSettingsPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
