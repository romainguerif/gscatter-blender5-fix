from typing import List, Union

import bpy

from ...common.ui import BasePanel
from ...utils.getters import (
    get_node_tree,
    get_wm_props,
    get_scene_props,
    get_scatter_item,
    get_preferences,
)
from ..ops.effect_layers import (
    AddEffectOperator,
    AddNewPresetOperator,
    ChangeEffectPresetOperator,
    DeleteEffectOperator,
    DuplicateEffectOperator,
    RemoveEffectPresetOperator,
    VisualizeOffOperator,
    VisualizeSelectedEffectOperator,
    VisualizeAllEffectOperator,
    AddExistingEffectOperator,
)
from ..props import EffectLayerProps
from ..utils import get_placeholders, can_visualize_selected_effect
from ..store import effectpresetstore, effectstore
from ... import icons
from ..utils import trees


class EffectLayerPanel(BasePanel):
    bl_idname = "GSCATTER_PT_effect_layer"
    bl_label = "Effect Layers"
    bl_parent_id = "GSCATTER_PT_scatter"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return get_node_tree(context)

    def draw_header(self, context: bpy.types.Context):
        self.layout.label(icon="NODETREE")

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        scene_props = get_scene_props(context)
        wm_props = get_wm_props(context)
        active_category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[active_category]
        get_preferences()

        # Check if node_tree is valid
        if not trees.is_node_tree_valid(node.node_tree):
            box = layout.box()
            box.alert = True
            box.label(text="Gscatter node tree is broken.", icon="ERROR")
            return

        ## Layout Visuailzer
        box = layout.box()
        col = box.column()
        row = col.split(factor=0.5)
        sub_row = row.row()
        sub_row.alignment = "LEFT"
        sub_row.prop(
            wm_props,
            "show_visualizer",
            text="Visualise Effect Layers",
            icon="TRIA_DOWN" if wm_props.show_visualizer else "TRIA_RIGHT",
            emboss=False,
        )
        # row.label(text="Visualise Effect Layers")
        row.prop(scene_props, "visualization_resolution", text="Resolution")

        if wm_props.show_visualizer:
            cannot_be_visualized = (
                scene_props.visualize_mode != "ALL"
                and not can_visualize_selected_effect(context, node_tree)
            )
            text = (
                "The selected effect does not support viewport visualization."
                if cannot_be_visualized
                else "Selected effect can be visualized."
                if not scene_props.visualizing
                else "Visualizing selected effect"
                if scene_props.visualize_mode == "SELECTED"
                else "Visualizing all effects."
            )
            icon = (
                "ERROR"
                if cannot_be_visualized
                else "visibility_off"
                if not scene_props.visualizing
                else "visibility_on"
            )
            if cannot_be_visualized:
                col.label(text=text, icon=icon)
            else:
                col.label(text=text, icon_value=icons.get(icon))
            row = col.row(align=True)
        else:
            row = row.row(align=True)

        row.operator(
            VisualizeOffOperator.bl_idname,
            text="Off",
            depress=scene_props.visualize_mode == "OFF",
        ).mode = "OFF"
        row.operator(
            VisualizeSelectedEffectOperator.bl_idname,
            text="Selected",
            depress=scene_props.visualize_mode == "SELECTED",
        ).mode = "SELECTED"
        row.operator(
            VisualizeAllEffectOperator.bl_idname,
            text="All",
            depress=scene_props.visualize_mode == "ALL",
        ).mode = "ALL"
        layout.separator()

        ## Layout Effects Categories
        scatter_item = get_scatter_item(context)
        if not scatter_item.is_terrain:
            layout.prop(scene_props, "active_category", expand=True)
            # layout.separator()

        self.draw_category(layout, context, active_category, node_tree)

        return

    def draw_category(self, layout, context, category, node):
        node_tree = node
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effect_list: List[EffectLayerProps] = node.node_tree.gscatter.effects
        selected: Union[EffectLayerProps, None] = node.node_tree.gscatter.get_selected()

        # Draw Add Effect Layer row
        row = layout.row(align=True)
        box = row.box()
        box.scale_y = 1.15
        row = box.row()

        sub_row = row.row(align=True)
        sub_rr = sub_row.row(align=True)
        sub_rr.scale_x = 1.3
        sub_rr.operator_menu_enum(
            AddExistingEffectOperator.bl_idname, "type", text="", icon="NODETREE"
        )
        # op.category = category  # TODO
        sub_row.operator_menu_enum(
            AddEffectOperator.bl_idname, "type", text="Add Effect Layer"
        )
        # op.category = category  # TODO
        row.popover(EffectPresetPanel.bl_idname, text="", icon="PRESET")
        # op.category = category  # TODO
        effect = None
        if selected:
            effect = effectstore.get_by_id_and_version(
                selected.get_effect_id(), selected.get_effect_version()
            )

        sub_row = row.row()
        sub_row.enabled = effect is not None
        sub_row.operator_menu_enum(
            DuplicateEffectOperator.bl_idname,
            property="target",
            text="",
            icon="DUPLICATE",
        )
        # op.category = category  # TODO
        row.operator(DeleteEffectOperator.bl_idname, text="", icon="TRASH")
        # op.category = category  # TODO

        # layout.separator(factor=0.1)

        #  Draw Mixing controls
        row = layout.row()
        row.scale_y = 0.8
        if not selected or selected.mix_node is None:
            row.enabled = False
            placeholders = get_placeholders()
            mixnode = next(
                node
                for node in placeholders.nodes
                if node.bl_idname == "ShaderNodeMixRGB"
            )
            row.prop(mixnode, "blend_type", text="")
            row.prop(mixnode.inputs[0], "default_value", text="Influence")
        else:
            rr = row.row()
            rr.alignment = "LEFT"
            rr.prop(selected, "blend_type", text="")
            row.prop(selected, "influence", text="Influence")
            rr = row.row()
            rr.alignment = "RIGHT"
            rr.prop(
                selected, "invert", text="Invert", icon="IMAGE_RGB_ALPHA", toggle=True
            )

        layout.separator(factor=0.1)

        # Draw Effects
        if len(effect_list) == 0:
            col = layout.box().column(align=True)
            col.active = False
            col.enabled = False
            row = col.row()
            row.alignment = "CENTER"
            row.label(text="No Effects to display,", icon="QUESTION")
            row = col.row()
            row.alignment = "CENTER"
            row.label(text="click Add Effect Layer at the top.")

        for effect in reversed(effect_list):
            effect.draw(layout, context)


class EffectPresetPanel(bpy.types.Panel):
    bl_idname = "GSCATTER_PT_effect_presets"
    bl_label = "Effect Presets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        scene_props = get_scene_props(context)
        category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effect: "EffectLayerProps" = node.node_tree.gscatter.get_selected()
        return True if effect else False

    def draw(self, context):
        layout = self.layout
        wm_props = get_wm_props(context)
        scene_props = get_scene_props(context)
        category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effect: "EffectLayerProps" = node.node_tree.gscatter.get_selected()

        presets = [
            preset
            for preset in effectpresetstore.get_by_effect_id(effect.get_effect_id())
            if preset.effect_version[0] == effect.get_effect_version()[0]
        ]

        col = layout.column(align=True)
        for preset in presets:
            row = col.row()
            row.operator(
                ChangeEffectPresetOperator.bl_idname, text=preset.name, emboss=False
            ).type = preset.id
            sub = row.row()
            sub.enabled = not preset.id.startswith("system.")
            sub.operator(
                RemoveEffectPresetOperator.bl_idname,
                text="",
                icon="REMOVE",
                emboss=False,
            ).type = preset.id

        row = layout.row()
        row.prop(wm_props, "new_preset", text="")
        row.operator(AddNewPresetOperator.bl_idname, text="", icon="ADD", emboss=False)


classes = (
    EffectPresetPanel,
    EffectLayerPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
