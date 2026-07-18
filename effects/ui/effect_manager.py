import bpy

from ...common.props import WindowManagerProps
from ...utils.getters import get_preferences
from ..ops.effect_manager import (
    CreateNewEffectOperator,
    DeleteEffectOperator,
    EditEffectNodeTreeOperator,
    ExportEffectOperator,
    ImportEffectOperator,
    SaveEffectInfoOperator,
    SaveEffectInSystemOperator,
    UpdateEffectOperator,
)
from ..props import EffectItemProps, EffectManagerProps, EffectProps, NodeInternalProps
from ..store import effectstore


class EffectList(bpy.types.UIList):
    bl_idname = "GSCATTER_UL_user_effect"

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item: EffectItemProps,
        icon,
        active_data,
        active_propname,
    ):
        wm_props: WindowManagerProps = context.window_manager.gscatter
        split = layout.split(
            factor=0.5
            if wm_props.effect_manager_props.effect_type_toggle == "USER"
            else 0.8
        )
        split.label(text=item.name)
        version_str = "v" + ".".join(map(str, item.version))
        if wm_props.effect_manager_props.effect_type_toggle != "USER":
            row = split.row()
            row.alignment = "RIGHT"
            row.label(text=version_str)
        else:
            split = split.split(factor=0.3)
            split.label(text=version_str)
            split.label(text=item.author)


class EffectsPanel(bpy.types.Panel):
    bl_idname = "GSCATTER_PT_effects"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "GScatter"
    bl_label = "Effects"

    def draw(self, context):
        prefs = get_preferences(context)
        wm_props: WindowManagerProps = context.window_manager.gscatter
        effect_manager_props: EffectManagerProps = wm_props.effect_manager_props

        wm_props.effect_items.clear()
        if len(wm_props.effect_items) == 0:
            for effect in sorted(
                effectstore.get_all(), key=lambda x: x.name, reverse=False
            ):
                if effect_manager_props.effect_type_toggle.lower() == effect.namespace:
                    effect_name: EffectItemProps = wm_props.effect_items.add()
                    effect_name.name = effect.name
                    effect_name.id = effect.id
                    effect_name.version = effect.effect_version
                    effect_name.author = effect.author
                # if effect_manager_props.effect_type_toggle.lower() != "system":
                #     if (
                #         effect_manager_props.effect_type_toggle.lower()
                #         == effect.namespace
                #     ):
                #         effect_name: EffectItemProps = wm_props.effect_items.add()
                #         effect_name.name = effect.name
                #         effect_name.id = effect.id
                #         effect_name.version = effect.effect_version
                #         effect_name.author = effect.author
                # else:
                #     if effect.namespace in [
                #         effect_manager_props.effect_type_toggle.lower(),
                #         "internal",
                #     ]:
                #         effect_name: EffectItemProps = wm_props.effect_items.add()
                #         effect_name.name = effect.name
                #         effect_name.id = effect.id
                #         effect_name.version = effect.effect_version
                #         effect_name.author = effect.author

        layout = self.layout

        row = layout.row()
        col = row.column(align=True)
        col.scale_y = 0.95
        r = col.row(align=True)
        # r.prop(effect_manager_props, "effect_type_toggle", expand=True)
        namespaces_items: bpy.types.EnumProperty.enum_items_static = (
            effect_manager_props.bl_rna.properties[
                "effect_type_toggle"
            ].enum_items_static
        )
        item: bpy.types.EnumPropertyItem
        for item in namespaces_items:
            # This is the first item of the enum item tuple, eg. "USER", or "SYSTEM", "INTERNAL" :
            namespace = item.identifier
            # This seems overkill but we need individual access to the field layout to disable it :
            if namespace == "USER" or prefs.enable_developer_mode:
                item_layout = r.row(align=True)
                item_layout.prop_enum(
                    effect_manager_props, "effect_type_toggle", namespace
                )

        col.separator()
        col.template_list(
            EffectList.bl_idname,
            "Effects",
            wm_props,
            "effect_items",
            wm_props,
            "effect_index",
            rows=6,
        )
        if prefs.enable_developer_mode:
            layout.operator("node.find_node")

        col = row.column(align=True)
        col.scale_y = col.scale_x = 1.05
        col.separator(factor=4)
        col.operator(
            CreateNewEffectOperator.bl_idname, text="", icon="ADD"
        ).namespace = effect_manager_props.effect_type_toggle.lower()
        col.operator(DeleteEffectOperator.bl_idname, text="", icon="REMOVE")
        col.separator()
        col.operator(EditEffectNodeTreeOperator.bl_idname, text="", icon="NODETREE")
        col.separator()
        col.operator(ImportEffectOperator.bl_idname, text="", icon="IMPORT")
        col.operator(ExportEffectOperator.bl_idname, text="", icon="EXPORT")


class EffectPropertiesPanel(bpy.types.Panel):
    bl_idname = "GSCATTER_PT_effect_properties"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "GScatter"
    bl_label = "Effect Properties"

    def draw(self, context):
        prefs = get_preferences(context)
        wm_props: WindowManagerProps = context.window_manager.gscatter
        effect_props: EffectProps = wm_props.effect_properties
        effect_manager_props: EffectManagerProps = wm_props.effect_manager_props
        layout = self.layout
        layout.use_property_split = True

        # if effect_manager_props.effect_type_toggle == "SYSTEM" and not prefs.enable_developer_mode:
        if effect_props.effect_id == "":
            layout.enabled = False

        effect_props.draw(layout, context)
        layout.separator(factor=0.6)
        col = layout.column()
        col.scale_y = 1.4
        r = col.row()
        r.alignment = "RIGHT"
        r.operator(
            UpdateEffectOperator.bl_idname, text="Update Effect", icon="DUPLICATE"
        )
        r.operator(
            SaveEffectInfoOperator.bl_idname, text="Save Effect Info", icon="INFO"
        )

        if (
            effect_manager_props.effect_type_toggle == "USER"
            and prefs.enable_developer_mode
        ):
            r.operator(SaveEffectInSystemOperator.bl_idname, icon="PACKAGE")


class NodePropertiesPanel(bpy.types.Panel):
    bl_idname = "GSCATTER_PT_node_properties"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "GScatter"
    bl_label = "Node Properties"

    @classmethod
    def poll(cls, context):
        return context.active_node is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        node_internal_props: NodeInternalProps = context.active_node.gscatter

        layout.prop(
            node_internal_props, "display_in_effect", text="Display node in effect UI"
        )
        box = layout.box()
        box.enabled = node_internal_props.display_in_effect
        col = box.column()
        col.prop(
            node_internal_props,
            "display_output_as_dropdown",
            text="Display Outputs as Dropdown",
        )
        col.prop(node_internal_props, "display_properties", text="Display Properties")
        col.prop(node_internal_props, "display_inputs", text="Display Inputs")
        layout.prop(node_internal_props, "display_order", text="Position")


class EffectManagerPanel(bpy.types.Panel):
    bl_idname = "GSCATTER_PT_effect_manager"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "GScatter"
    bl_label = "Effect Manager"

    @classmethod
    def poll(cls, context):
        prefs = get_preferences(context)
        return prefs.enable_experimental_features

    def draw(self, context: bpy.types.Context):
        prefs = get_preferences(context)
        layout = self.layout
        layout.use_property_split = True

        layout.operator("node.find_node")

        wm_props: WindowManagerProps = context.window_manager.gscatter

        wm_props.effect_items.clear()

        if len(wm_props.effect_items) == 0:
            for effect in sorted(
                effectstore.get_all(), key=lambda x: x.name, reverse=False
            ):
                effect_name: EffectItemProps = wm_props.effect_items.add()
                effect_name.name = effect.name
                effect_name.id = effect.id
                effect_name.version = effect.effect_version

        layout.template_list(
            EffectList.bl_idname,
            "User Effects",
            wm_props,
            "effect_items",
            wm_props,
            "effect_index",
        )

        layout.separator()
        wm_props.effect_properties.draw(layout, context)
        layout.separator()
        if prefs.enable_developer_mode:
            layout.separator()
            layout.label(text="You are in Developer mode", icon="FAKE_USER_ON")
        layout.operator(
            CreateNewEffectOperator.bl_idname,
            text=f"Create New Effect {'in User' if prefs.enable_developer_mode else ''}",
            icon="ADD",
        ).namespace = "user"
        if prefs.enable_developer_mode:
            layout.operator(
                CreateNewEffectOperator.bl_idname,
                text="Create New Effect in System",
                icon="ADD",
            ).namespace = "system"
        layout.operator(
            UpdateEffectOperator.bl_idname,
            text="Update Selected Effect",
            icon="DUPLICATE",
        )
        layout.operator(
            ImportEffectOperator.bl_idname,
            text="Install Effect from File",
            icon="IMPORT",
        )
        layout.operator(
            ExportEffectOperator.bl_idname, text="Export Effect", icon="EXPORT"
        )
        layout.operator(
            DeleteEffectOperator.bl_idname, text="Delete Effect", icon="TRASH"
        )
        layout.separator()
        n = context.active_node
        if n is not None:
            layout.prop(n.gscatter, "display_in_effect", text="Add to effect UI")
            layout.prop(n.gscatter, "display_order", text="Draw order")


classes = (
    EffectList,
    EffectsPanel,
    EffectPropertiesPanel,
    NodePropertiesPanel,
    # EffectManagerPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
