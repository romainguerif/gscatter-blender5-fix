from typing import Protocol
from .. import icons
import bpy

from .utils import get_icon_viewer_props


class IconViewerTarget(Protocol):
    icon: str


class IconViewerPopup(bpy.types.Operator):
    bl_idname = "gscatter.popup_icon_viewer"
    bl_label = "GScatter Icon Viewer"
    bl_description = "Choose from available icons"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    target: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        icon_viewer_props = get_icon_viewer_props(context)
        target: IconViewerTarget = eval(self.target)

        icon_viewer_props.update(context)
        icon_viewer_props.select(target.icon)

        return context.window_manager.invoke_props_dialog(
            self, width=icon_viewer_props.width
        )

    def execute(self, context: bpy.types.Context) -> set[str]:
        icon_viewer_props = get_icon_viewer_props(context)
        target: IconViewerTarget = eval(self.target)

        if target.icon != icon_viewer_props.selected:
            self.report({"INFO"}, f"Set icon to {icon_viewer_props.selected}")

        target.icon = icon_viewer_props.selected
        return {"FINISHED"}

    def draw(self, context: bpy.types.Context):
        icon_viewer_props = get_icon_viewer_props(context)
        icon_viewer_props.draw(self.layout)


class SelectIconOperator(bpy.types.Operator):
    bl_idname = "gscatter.select_icon"
    bl_label = "Select Icon"
    bl_options = {"REGISTER", "INTERNAL"}

    icon: bpy.props.StringProperty()

    @classmethod
    def description(
        cls, context: bpy.types.Context, properties: bpy.types.OperatorProperties
    ) -> str:
        return properties["icon"]

    def execute(self, context: bpy.types.Context) -> set[str]:
        icon_viewer_props = get_icon_viewer_props(context)
        icon_viewer_props.select(self.icon)
        return {"FINISHED"}


class ReloadIconsOperator(bpy.types.Operator):
    bl_idname = "gscatter.reload_icons"
    bl_label = "Reload Icons"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        icons.load_user_icons()
        self.report({"INFO"}, message="Reloaded icons")
        return {"FINISHED"}


classes = (
    ReloadIconsOperator,
    IconViewerPopup,
    SelectIconOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
