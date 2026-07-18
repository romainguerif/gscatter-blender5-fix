from pathlib import Path
from uuid import uuid4

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper

from ...utils.getters import get_preferences
from .. import default
from ..props import WindowManagerProps
from ..store import effectstore
from ..store.effect_item import Effect
from ..utils.trees import create_template_effect_node_tree


class ImportEffectOperator(bpy.types.Operator, ImportHelper):
    """Imports an effect from file"""

    bl_idname = "gscatter.import_effect_manager"
    bl_label = "Import"
    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})  # type: ignore
    files: bpy.props.CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )  # type: ignore
    directory: bpy.props.StringProperty(
        subtype="DIR_PATH",
    )  # type: ignore

    def execute(self, context: bpy.types.Context):
        directory = self.directory
        for file_elem in self.files:
            file_path = Path(directory, file_elem.name)
            effectstore.add_from_filepath(file_path.as_posix())
            self.report({"INFO"}, message="Effect imported.")
        return {"FINISHED"}


class UpdateEffectOperator(bpy.types.Operator):
    """Update an existing effect"""

    bl_idname = "gscatter.update_effect_manager"
    bl_label = "Update"
    bl_description: str = "Update an effect"

    @classmethod
    def poll(cls, context):
        prefs = get_preferences(context)
        wm_props: WindowManagerProps = context.window_manager.gscatter
        index = wm_props.effect_index
        try:
            effect_id = wm_props.effect_items[index].id
        except IndexError:
            return False
        effect_version = wm_props.effect_items[index].version
        effect = effectstore.get_by_id_and_version(effect_id, effect_version)

        if effect is None:
            return False

        if (
            effect.namespace in ["system", "internal"]
            and not prefs.enable_developer_mode
        ):
            return False

        node = context.active_node
        return isinstance(node, bpy.types.GeometryNodeGroup)

    def execute(self, context: bpy.types.Context):
        wm_props: WindowManagerProps = bpy.context.window_manager.gscatter
        node = context.active_node

        if isinstance(node, bpy.types.GeometryNodeGroup):
            index = wm_props.effect_index
            effect_id = wm_props.effect_items[index].id
            effect_version = wm_props.effect_items[index].effect_version.original
            effect_props = wm_props.effect_properties

            effect = effectstore.get_by_id_and_version(effect_id, effect_version)

            effect.name = effect_props.name
            effect.author = effect_props.author
            effect.description = effect_props.description
            effect.icon = effect_props.icon
            effect.categories = effect_props.categories
            effect.subcategory = effect_props.subcategory
            effect.effect_version = effect_props.version
            effect.schema_version = default.EFFECT_SCHEMA_VERSION
            effect.blender_version = effect_props.blender_app_version
            effect.nodetree = node.node_tree
            effect.blend_types = effect_props.blend_types.get_enabled()
            effect.default_blend_type = effect_props.default_blend_type

            context.active_node.label = effect.name
            # context.active_node.node_tree.name = effect.name

            effectstore.update(effect_version, effect)

            bpy.context.view_layer.update()
            effects = sorted(effectstore.get_all(), key=lambda x: x.name, reverse=False)
            if wm_props.effect_manager_props.effect_type_toggle.lower() == "system":
                effects = [
                    e
                    for e in effects
                    if e.namespace
                    in [
                        wm_props.effect_manager_props.effect_type_toggle.lower(),
                        "internal",
                    ]
                ]
            else:
                effects = [
                    e
                    for e in effects
                    if e.namespace
                    == wm_props.effect_manager_props.effect_type_toggle.lower()
                ]
            for i, effect_item in enumerate(effects):
                if effect_item.id == effect.id:
                    wm_props.effect_index = i
                    wm_props.effect_properties.set(effect)
                    break

        else:
            self.report("ERROR", "Node is not a group node. Cannot save.")
            return {"CANCELLED"}
        self.report({"INFO"}, message="Updated effect")
        return {"FINISHED"}


class SaveEffectInSystemOperator(bpy.types.Operator):
    """Saves a user effect in system"""

    bl_idname: str = "gscatter.save_in_system"
    bl_label: str = "Save in system"

    @classmethod
    def poll(cls, context):
        prefs = get_preferences(context)
        if not prefs.enable_developer_mode:
            return False
        wm_props: WindowManagerProps = context.window_manager.gscatter
        index = wm_props.effect_index
        try:
            wm_props.effect_items[index].id
        except IndexError:
            return False
        return True

    def execute(self, context):
        wm_props: WindowManagerProps = context.window_manager.gscatter

        index = wm_props.effect_index
        new_effect_id = uuid4().hex
        effect_id = wm_props.effect_items[index].id
        effect_version = wm_props.effect_items[index].effect_version.original

        effect = effectstore.get_by_id_and_version(effect_id, effect_version)
        effect.id = new_effect_id
        effectstore.add("system", effect)

        self.report({"INFO"}, message="Saved effect as a system effect.")
        return {"FINISHED"}


class CreateNewEffectOperator(bpy.types.Operator):
    """Create a new effect"""

    bl_idname: str = "gscatter.create_effect_manager"
    bl_label: str = "Create Effect"

    namespace: bpy.props.StringProperty(name="Namespace", default="user")  # type: ignore

    @classmethod
    def poll(cls, context):
        prefs = get_preferences(context)
        wm_props: WindowManagerProps = context.window_manager.gscatter
        if context.object is None:
            return False
        active_modifier = context.object.modifiers.active
        if active_modifier and active_modifier.type == "NODES":
            if active_modifier.node_group:
                pass
            else:
                return False
        else:
            return False
        if (
            wm_props.effect_manager_props.effect_type_toggle in ["SYSTEM", "INTERNAL"]
            and not prefs.enable_developer_mode
        ):
            return False
        return True

    def execute(self, context):
        wm_props: WindowManagerProps = context.window_manager.gscatter
        effects = [
            effect
            for effect in effectstore.get_all()
            if effect.namespace == self.namespace
        ]
        effect_name = f"New Effect {len(effects) + 1}"

        effect_id = str(uuid4())

        template_node_group = create_template_effect_node_tree()

        effect = Effect(
            effect_id,
            effect_name,
            "Your Name",
            "Effect description here.",
            "SHADERFX",
            ["DISTRIBUTION"],
            "Basic",
            [1, 0, 0],
            default.EFFECT_SCHEMA_VERSION,
            list(bpy.app.version),
            template_node_group,
        )
        effectstore.add(self.namespace, effect)
        bpy.data.node_groups.remove(template_node_group)
        # Create a node_group and add it to the current node_view
        active_modifier = context.object.modifiers.active
        if active_modifier and active_modifier.type == "NODES":
            if active_modifier.node_group:
                bpy.ops.node.select_all(action="TOGGLE")
                new_node: bpy.types.GeometryNodeGroup = (
                    context.space_data.edit_tree.nodes.new("GeometryNodeGroup")
                )
                new_node.node_tree = effect.nodetree
                new_node.select = True
                context.space_data.edit_tree.nodes.active = new_node
                bpy.context.view_layer.update()
                bpy.ops.node.view_selected("INVOKE_DEFAULT")

        bpy.context.view_layer.update()
        effects = sorted(effectstore.get_all(), key=lambda x: x.name, reverse=False)
        for i, effect_item in enumerate(
            [
                e
                for e in effects
                if e.namespace
                == wm_props.effect_manager_props.effect_type_toggle.lower()
            ]
        ):
            if effect_item.id == effect.id:
                wm_props.effect_index = i
                break
        wm_props.effect_properties.set(effect)
        self.report({"INFO"}, message="Created a new effect.")
        return {"FINISHED"}


class ExportEffectOperator(bpy.types.Operator, ExportHelper):
    """Exports an effect to file"""

    bl_idname = "gscatter.export_effect_manager"
    bl_label = "Export"

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        prefs = get_preferences(context)
        wm_props: WindowManagerProps = context.window_manager.gscatter
        index = wm_props.effect_index
        try:
            effect_item = wm_props.effect_items[index]
        except IndexError:
            return False
        effect_id = effect_item.id
        effect_version = effect_item.version
        effect = effectstore.get_by_id_and_version(effect_id, effect_version)

        if effect is None:
            return False

        if (
            effect.namespace in ["system", "internal"]
            and not prefs.enable_developer_mode
        ):
            return False
        return True

    def execute(self, context: bpy.types.Context):
        wm_props: WindowManagerProps = context.window_manager.gscatter
        effect_props = wm_props.effect_properties
        effect = effectstore.get_by_id_and_version(
            effect_props.effect_id, effect_props.version
        )
        if effect:
            effect.export(self.filepath)
            self.report({"INFO"}, message="Effect exported")
        else:
            self.report({"WARNING"}, message="Effect not found")
        return {"FINISHED"}


class DeleteEffectOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.delete_effect_manager"
    bl_label: str = "Delete Effect"
    bl_description: str = "Delete an effect"

    index = 0

    @classmethod
    def poll(cls, context):
        prefs = get_preferences(context)
        wm_props: WindowManagerProps = context.window_manager.gscatter
        index = wm_props.effect_index
        try:
            effect_item = wm_props.effect_items[index]
        except IndexError:
            return False
        effect_id = effect_item.id
        effect_version = effect_item.version
        effect = effectstore.get_by_id_and_version(effect_id, effect_version)

        if effect is None:
            return False

        if (
            effect.namespace in ["system", "internal"]
            and not prefs.enable_developer_mode
        ):
            return False
        return True

    def invoke(self, context, event):
        self.index = context.window_manager.gscatter.effect_index - 1
        if self.index <= 0:
            self.index = 0
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        wm_props: WindowManagerProps = context.window_manager.gscatter
        i = wm_props.effect_index
        effect_id = wm_props.effect_items[i].id
        effect_version = wm_props.effect_items[i].version
        wm_props.effect_index = self.index
        effectstore.remove(effectstore.get_by_id_and_version(effect_id, effect_version))
        self.report({"INFO"}, message="Effect Deleted")
        return {"FINISHED"}


class EditEffectNodeTreeOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.edit_effect_tree"
    bl_label: str = "Edit Effect Node Tree"
    bl_description: str = "Edit an effects node tree"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.object is None:
            return False
        active_modifier = context.object.modifiers.active
        if active_modifier and active_modifier.type == "NODES":
            if active_modifier.node_group:
                pass
            else:
                return False
        else:
            return False

        prefs = get_preferences(context)
        wm_props: WindowManagerProps = context.window_manager.gscatter
        index = wm_props.effect_index
        try:
            effect_item = wm_props.effect_items[index]
        except IndexError:
            return False
        effect_id = effect_item.id
        effect_version = effect_item.version
        effect = effectstore.get_by_id_and_version(effect_id, effect_version)

        if effect is None:
            return False

        if (
            effect.namespace in ["system", "internal"]
            and not prefs.enable_developer_mode
        ):
            return False
        return True

    def execute(self, context):
        wm_props: WindowManagerProps = context.window_manager.gscatter
        index = wm_props.effect_index
        try:
            effect_item = wm_props.effect_items[index]
        except IndexError:
            return False
        effect_id = effect_item.id
        effect_version = effect_item.version
        effect = effectstore.get_by_id_and_version(effect_id, effect_version)

        # Create a node_group and add it to the current node_view
        active_modifier = context.object.modifiers.active
        if active_modifier and active_modifier.type == "NODES":
            if active_modifier.node_group:
                new_node: bpy.types.GeometryNodeGroup = (
                    context.space_data.edit_tree.nodes.new("GeometryNodeGroup")
                )
                new_node.node_tree = effect.nodetree
                bpy.ops.node.select_all(action="TOGGLE")
                new_node.select = True
                context.space_data.edit_tree.nodes.active = new_node
                bpy.context.view_layer.update()
                bpy.ops.node.view_selected("INVOKE_DEFAULT")
        return {"FINISHED"}


class SaveEffectInfoOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.save_effect_info"
    bl_label: str = "Save Effect Info"
    bl_description: str = "Save an effect info"

    @classmethod
    def poll(cls, context):
        prefs = get_preferences(context)
        wm_props: WindowManagerProps = context.window_manager.gscatter
        index = wm_props.effect_index
        try:
            effect_id = wm_props.effect_items[index].id
        except IndexError:
            return False
        effect_version = wm_props.effect_items[index].version
        effect = effectstore.get_by_id_and_version(effect_id, effect_version)

        if effect is None:
            return False

        if (
            effect.namespace in ["system", "internal"]
            and not prefs.enable_developer_mode
        ):
            return False
        return True

    def execute(self, context: bpy.types.Context):
        wm_props: WindowManagerProps = bpy.context.window_manager.gscatter

        index = wm_props.effect_index
        effect_id = wm_props.effect_items[index].id
        effect_version = wm_props.effect_items[index].effect_version.original
        effect_props = wm_props.effect_properties

        effect = effectstore.get_by_id_and_version(effect_id, effect_version)

        effect.name = effect_props.name
        effect.author = effect_props.author
        effect.description = effect_props.description
        effect.icon = effect_props.icon
        effect.categories = effect_props.categories
        effect.subcategory = effect_props.subcategory
        effect.effect_version = effect_props.version
        effect.schema_version = default.EFFECT_SCHEMA_VERSION
        effect.blender_version = effect_props.blender_app_version
        effect.blend_types = effect_props.blend_types.get_enabled()
        effect.default_blend_type = effect_props.default_blend_type

        # context.active_node.node_tree.name = effect.name

        effectstore.update(effect_version, effect)

        bpy.context.view_layer.update()
        effects = sorted(effectstore.get_all(), key=lambda x: x.name, reverse=False)
        if wm_props.effect_manager_props.effect_type_toggle.lower() == "system":
            effects = [
                e
                for e in effects
                if e.namespace
                in [
                    wm_props.effect_manager_props.effect_type_toggle.lower(),
                    "internal",
                ]
            ]
        else:
            effects = [
                e
                for e in effects
                if e.namespace
                == wm_props.effect_manager_props.effect_type_toggle.lower()
            ]
        for i, effect_item in enumerate(effects):
            if effect_item.id == effect.id:
                wm_props.effect_index = i
                wm_props.effect_properties.set(effect)
                break

        self.report({"INFO"}, message="Updated effect")
        return {"FINISHED"}


classes = (
    ImportEffectOperator,
    ExportEffectOperator,
    UpdateEffectOperator,
    CreateNewEffectOperator,
    DeleteEffectOperator,
    EditEffectNodeTreeOperator,
    SaveEffectInSystemOperator,
    SaveEffectInfoOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
