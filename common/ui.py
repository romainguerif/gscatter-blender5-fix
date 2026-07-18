import bpy

from .. import utils
from .ops import CloseCompatibilityWarningOperator
from .props import WindowManagerProps

_COMPATIBILITY_MSG = "Blender version {} might not be supported. Please use either Blender version 3.5 - 4.5 stable and upwards."


class BasePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GScatter"


class CompatibilityPanel(BasePanel):
    bl_idname = "GSCATTER_PT_compatibility"
    bl_label = "Compatibility Warning"
    bl_order = 70

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        prefs = utils.getters.get_preferences()
        wm_props: WindowManagerProps = context.window_manager.gscatter
        return (
            (not prefs.ignore_compatibility_warning)
            and not wm_props.compatibility_warning
            and not (bpy.app.version >= (3, 5, 0) or bpy.app.version <= (4, 5, 0))
            and (
                bpy.app.version_string.endswith("Alpha")
                or bpy.app.version_string.endswith("Beta")
            )
        )

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        box = layout.box()
        text_col = box.column(align=True)
        text_col.scale_y = 1.2
        width = context.region.width
        for text in utils.wrap_text(
            _COMPATIBILITY_MSG.format(bpy.app.version_string), width
        ):
            text_col.label(text=text)
        row = layout.row()
        row.scale_y = 1.5
        row = layout.row()
        wm_props: WindowManagerProps = context.window_manager.gscatter
        row.prop(
            wm_props,
            "ignore_compatibility_warning",
            text="Do not show this message again",
        )
        row = layout.row()
        row.operator(CloseCompatibilityWarningOperator.bl_idname)


classes = (CompatibilityPanel,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
