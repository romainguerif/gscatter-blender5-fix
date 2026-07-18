import bpy
from ..common.ui import BasePanel
from .ops import RealizeSystemOperator, ApplySystemOperator


class UtilitiesPanel(BasePanel):
    bl_idname = "GSCATTER_PT_utilities"
    bl_label = "Extras"
    bl_order = 180
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == "OBJECT"

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(icon="TOOL_SETTINGS")

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        row.operator("file.pack_all", text="Pack blend file", icon="GROUP")
        row = col.row()
        row.operator(
            "file.pack_libraries", text="Pack linked Assets", icon="DECORATE_LINKED"
        )

        row = col.row()
        sub_col = row.column()
        row = sub_col.row()
        row.operator(
            RealizeSystemOperator.bl_idname,
            text="Realize Selected Scatter System",
            icon="STICKY_UVS_DISABLE",
        )
        row = sub_col.row()
        row.operator(
            ApplySystemOperator.bl_idname,
            text="Apply Selected Scatter System",
            icon="STICKY_UVS_LOC",
        )


classes = (UtilitiesPanel,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
