from typing import TYPE_CHECKING

import bpy

from ...utils.logger import debug
from ..configurators import configure
from ...utils import main_collection, getters

if TYPE_CHECKING:
    from ...common.props import WindowManagerProps
    from ..props.library import LibraryWidget


class DummyOperator(bpy.types.Operator):
    bl_idname = "gscatter.dummy"
    bl_label = "Dummy Operator"
    bl_description = "Does nothing when pressed"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> set:
        return {"CANCELLED"}


class SelectItemOperator(bpy.types.Operator):
    bl_idname = "gscatter.select_item"
    bl_label = "Select Item"
    bl_description = "Select or deselect an item"
    bl_options = {"REGISTER", "INTERNAL"}

    target: bpy.props.StringProperty(name="Target")
    deselect: bpy.props.BoolProperty(name="Deselect")

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set:
        target = eval(self.target)
        library: "LibraryWidget" = target.parent
        collection = target.parent_collection

        if self.deselect:
            target.select = False
        elif event.shift and library.browse_type == "ASSETS":
            target.select = not target.select
        else:
            for item in collection:
                item.select = False
            target.select = True

        if collection == library.assets:
            library.refresh_configurators()

            if not self.deselect:
                assets = library.filtered_assets()
                index = assets.index(target)
                library.focus_asset(index)

        elif collection == library.tags:
            library.update_search(context)

        return {"FINISHED"}


class UseItemOperator(bpy.types.Operator):
    bl_idname = "gscatter.use_item"
    bl_label = "Use Item"
    bl_description = "Use selected item"
    bl_options = {"REGISTER", "INTERNAL"}

    target: bpy.props.StringProperty(name="Target")
    effect_name: bpy.props.StringProperty()
    input_name: bpy.props.StringProperty()

    def execute(self, context):
        scene_props = getters.get_scene_props(context)
        category: str = scene_props.active_category
        node_tree = getters.get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effects: bpy.types.bpy_prop_collection = node.node_tree.gscatter.effects
        effect = effects[self.effect_name]

        source = main_collection(sub="Sources")
        target = eval(self.target)

        col = configure(target)
        if col.name not in source.children:
            source.children.link(col)
        col.gscatter.is_gscatter_asset = True
        col.gscatter.asset_id = target.asset_id

        input = effect.effect_node.inputs.get(self.input_name)
        if input:
            input.default_value = col
        else:
            debug("Input not found")
        bpy.context.window.screen = bpy.context.window.screen
        return {"FINISHED"}


class ClearTagsOperator(bpy.types.Operator):
    bl_idname = "gscatter.clear_tags"
    bl_label = "Clear Tags"
    bl_description = "Deselect all tags"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> set:
        G: "WindowManagerProps" = context.window_manager.gscatter
        library: "LibraryWidget" = G.library

        for tag in library.tags:
            tag.select = False

        library.update_search(context)

        return {"FINISHED"}


class ScrollDetailsOperator(bpy.types.Operator):
    bl_idname = "gscatter.scroll_details"
    bl_label = "Scroll Details"
    bl_description = "Scroll through preview images"
    bl_options = {"REGISTER", "INTERNAL"}

    previews: bpy.props.StringProperty(name="Previews")
    direction: bpy.props.IntProperty(name="Direction")

    def execute(self, context: bpy.types.Context) -> set:
        previews = eval(self.previews)

        previews.index += self.direction
        previews.index %= len(previews.details)

        return {"FINISHED"}


classes = (
    DummyOperator,
    SelectItemOperator,
    ClearTagsOperator,
    ScrollDetailsOperator,
    UseItemOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
