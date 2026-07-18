from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ...common.props import WindowManagerProps
    from ..props.library import LibraryWidget


class SelectPageOperator(bpy.types.Operator):
    bl_idname = "gscatter.select_page"
    bl_label = "Select Page"
    bl_description = "Select the active page in the asset browser"
    bl_options = {"REGISTER", "INTERNAL"}

    index: bpy.props.IntProperty(name="Index")

    def execute(self, context: bpy.types.Context) -> set:
        G: "WindowManagerProps" = context.window_manager.gscatter
        library: "LibraryWidget" = G.library
        library.page = self.index

        return {"FINISHED"}


class ScrollPageLeftOperator(bpy.types.Operator):
    bl_idname = "gscatter.scroll_page_left"
    bl_label = "Scroll Page Left"
    bl_description = "Scroll the pages of the asset browser"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> set:
        G: "WindowManagerProps" = context.window_manager.gscatter
        library: "LibraryWidget" = G.library
        library.page -= 1

        return {"FINISHED"}


class ScrollPageRightOperator(bpy.types.Operator):
    bl_idname = "gscatter.scroll_page_right"
    bl_label = "Scroll Page Right"
    bl_description = "Scroll the pages of the asset browser"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> set:
        G: "WindowManagerProps" = context.window_manager.gscatter
        library: "LibraryWidget" = G.library
        library.page += 1

        return {"FINISHED"}


classes = (
    SelectPageOperator,
    ScrollPageLeftOperator,
    ScrollPageRightOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
