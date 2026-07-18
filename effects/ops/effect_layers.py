import itertools
from typing import TYPE_CHECKING, Any, List, Tuple, Union
from uuid import uuid4
import bpy
from bpy.types import Context

from ...utils.logger import debug, info
from ...utils.getters import (
    get_node_tree,
    get_scatter_surface,
    get_scatter_system,
    get_wm_props,
    get_scatter_item,
    get_scene_props,
    get_system_tree,
    get_effect_data,
)
from .. import default, utils
from ..store.effect_preset import EffectPreset
from ..store import effectpresetstore, effectstore
from ..utils.setter import (
    set_dropdown,
    set_layer_params,
    set_node_props,
    set_params,
)
from ... import icons

# from functools import partial
# from ..utils.trees import update_subivide_node
from ...utils import main_collection

if TYPE_CHECKING:
    from ..props import EffectLayerProps
# TODO: Import these once we drop 2.93 support.
NON_PRIMITIVE_SOCKETS = {
    "NodeSocketGeometry",
    "NodeSocketMaterial",
    "NodeSocketTexture",
}

scatter_surface: bpy.types.Object = None
space_data = None
surfaces_hidden = []


class VisualizeEffectOperator(bpy.types.Operator):
    bl_idname = "gscatter.visualize_effect"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_label = "Visualize Effect"
    bl_description = "Visualize a single effect or all effects"

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("OFF", "Off", "Visualize mode off", "", 0),
            ("ALL", "All Effects", "Visualize all effects", "", 1),
            ("SELECTED", "Selected", "Visualize selected effect", "", 2),
        ],
        default="OFF",
    )

    selected_effect = ""
    selected_category = ""
    visualize_object = None
    scatter_item = None
    _timer = None
    effects = 0
    scatter_items_length = 0

    viz_mode = None

    def unhide_and_clear_surfaces(self):
        global surfaces_hidden
        for surface in surfaces_hidden:
            try:
                surface.hide_set(False)
            except Exception:
                continue
        surfaces_hidden.clear()

    def add_surfaces(self, viz_copy_tree):
        global surfaces_hidden
        for link in viz_copy_tree.nodes["Join System"].inputs[0].links:
            system = link.from_node.inputs[0].default_value
            system.hide_set(True)
            surfaces_hidden.append(system)

    def modal(self, context, event):
        global surfaces_hidden

        scene_props = get_scene_props(context)
        ss = get_scatter_surface(context)
        scatter_system = get_scatter_system(context)
        if ss is None or scatter_system is None:
            return self.execute(context)

        category = scene_props.active_category
        main_tree = get_node_tree(context)
        system_tree = get_system_tree(context)
        node: bpy.types.GeometryNodeGroup = main_tree.nodes[category]
        selected = node.node_tree.gscatter.get_selected()
        si = get_scatter_item(context)

        # Turn off visualization
        if not scene_props.visualizing or self.visualize_object != ss:
            return self.execute(context)

        if self.scatter_items_length < len(ss.gscatter.scatter_items):
            return self.execute(context)

        if self.selected_category != category:
            self.selected_category = category
            utils.toggle_visualization(main_tree)

        if self.effects != len(node.node_tree.gscatter.effects):
            self.effects = len(node.node_tree.gscatter.effects)
            utils.toggle_visualization(main_tree)

        if self.scatter_item != si:
            viz_copy_tree = utils.create_viz_node_tree(main_tree, ss, si)
            self.scatter_item = si
            utils.toggle_visualization(main_tree)
            self.unhide_and_clear_surfaces()
            self.add_surfaces(viz_copy_tree)

        join_geom_main = system_tree.nodes["Join Geometry"]
        viz_copy_name = si.obj.name + "_viz_copy"
        viz_copy_tree = bpy.data.node_groups.get(viz_copy_name)

        if viz_copy_tree:
            join_geom_viz = viz_copy_tree.nodes["Join System"]
            utils.update_viz_surfaces(
                viz_copy_tree, join_geom_main, join_geom_viz, surfaces_hidden
            )
        else:
            debug("GScatter: No viz_copy_tree found. Creating new copy")
            viz_copy_tree = utils.create_viz_node_tree(main_tree, ss, si)
            join_geom_viz = viz_copy_tree.nodes["Join System"]
            utils.update_viz_surfaces(
                viz_copy_tree, join_geom_main, join_geom_viz, surfaces_hidden
            )
            self.unhide_and_clear_surfaces()
            self.add_surfaces(viz_copy_tree)

        if self.scatter_items_length != len(ss.gscatter.scatter_items):
            self.unhide_and_clear_surfaces()
            si = get_scatter_item(context)
            self.scatter_item = si
            viz_copy_tree = utils.create_viz_node_tree(main_tree, ss, si)
            join_geom_viz = viz_copy_tree.nodes["Join System"]
            utils.update_viz_surfaces(
                viz_copy_tree, join_geom_main, join_geom_viz, surfaces_hidden
            )

            self.add_surfaces(viz_copy_tree)
            utils.toggle_visualization(main_tree)
            self.scatter_items_length = len(ss.gscatter.scatter_items)

        if (
            scene_props.visualize_mode == "SELECTED"
            and selected != self.selected_effect
        ):
            self.selected_effect = selected
            utils.toggle_visualization(main_tree)

        return {"PASS_THROUGH"}

    def invoke(self, context: Context, event):
        global scatter_surface
        global space_data
        global surfaces_hidden

        global shading_light
        global shading_color_type

        scene_props = get_scene_props(context)
        category = scene_props.active_category
        main_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = main_tree.nodes[category]
        self.visualize_object = get_scatter_surface(context)
        main_tree.nodes.get("GEOMETRY")
        main_tree.nodes.get("Join Geometry")

        if scene_props.visualize_mode == self.mode:
            debug("GScatter: Already in current mode")
            return {"CANCELLED"}
        scatter_surface = scene_props.scatter_surface
        scatter_surface.hide_set(True)

        self.scatter_item = get_scatter_item(context)

        # Create a viz node_group copy of current system
        viz_copy_tree = utils.create_viz_node_tree(
            main_tree, scatter_surface, self.scatter_item
        )

        if self.mode == "OFF":
            return self.execute(context)

        self.selected_category = category

        scene_props.visualize_mode = self.mode
        utils.toggle_visualization(main_tree)
        self.selected_effect = node.node_tree.gscatter.get_selected()
        self.effects = len(node.node_tree.gscatter.effects)
        self.scatter_items_length = len(scatter_surface.gscatter.scatter_items)

        self.add_surfaces(viz_copy_tree)

        if scene_props.visualizing:
            return {"FINISHED"}

        scene_props.visualizing = True
        space_data = bpy.context.space_data

        shading_light = space_data.shading.light
        shading_color_type = space_data.shading.color_type

        space_data.shading.light = "FLAT"
        space_data.shading.color_type = "VERTEX"

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        global surfaces_hidden
        global space_data

        global shading_light
        global shading_color_type

        bpy.context.view_layer.update()
        wm_props = get_wm_props(context)
        scene_props = get_scene_props(context)
        if not scene_props.visualizing:
            return {"CANCELLED"}
        main_tree = get_node_tree(context)
        si = get_scatter_item(context)
        wm_props.can_be_visualized = True
        scene_props.visualizing = False
        scene_props.visualize_mode = "OFF"
        if space_data is None:
            space_data = bpy.context.space_data
        if hasattr(space_data, "shading"):
            if shading_light == "":
                space_data.shading.light = "STUDIO"
            else:
                space_data.shading.light = shading_light
            if shading_color_type == "":
                space_data.shading.color_type = "OBJECT"
            else:
                space_data.shading.color_type = shading_color_type

        if main_tree:
            utils.trees.connect_last_node_to_visualize_output(main_tree)
            utils.toggle_visualization(main_tree)

            viz_copy_name = si.obj.name + "_viz_copy"
            viz_copy_tree = bpy.data.node_groups.get(viz_copy_name)
            if viz_copy_tree:
                for link in viz_copy_tree.nodes["Join System"].inputs[0].links:
                    system = link.from_node.inputs[0].default_value
                    system.hide_set(False)

        utils.trees.disconnect_all_geometry_outputs(context)
        utils.reset_colors()

        if surfaces_hidden:
            for surface in surfaces_hidden:
                try:
                    surface.hide_set(False)
                except Exception:
                    continue
        else:
            if scene_props.scatter_surface:
                scene_props.scatter_surface.hide_set(False)

        main = main_collection()
        viz_col = main_collection(sub="Visualizer")
        for view_layer in context.scene.view_layers:
            view_layer.layer_collection.children[main.name].children[
                viz_col.name
            ].exclude = True

        for node in bpy.data.node_groups:
            if node.name.endswith("_viz_copy"):
                bpy.data.node_groups.remove(node)
        self.report({"INFO"}, message="Visualization stopped.")
        info("GScatter: Visualization stopped")
        return {"FINISHED"}


class VisualizeSelectedEffectOperator(VisualizeEffectOperator):
    bl_idname = "gscatter.visualize_selected_effect"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_label = "Visualize Selected"
    bl_description = "Visualize only the selected Effect Layer"

    @classmethod
    def poll(cls, context):
        return utils.can_visualize_selected_effect(context)


class VisualizeAllEffectOperator(VisualizeEffectOperator):
    bl_idname = "gscatter.visualize_all_effect"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_label = "Visualize All Effect"
    bl_description = "Visualize all effects"

    @classmethod
    def poll(cls, context):
        scene_props = get_scene_props(context)
        item = get_scatter_item(context)
        category = scene_props.active_category
        if not (
            item
            and item.get_ntree_version() >= (2, 1, 0)
            and category in ["DISTRIBUTION", "SCALE"]
        ):
            return False
        return True


class VisualizeOffOperator(VisualizeEffectOperator):
    bl_idname = "gscatter.visualize_off"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_label = "Visualize off"
    bl_description = "Turn off Visualization"

    @classmethod
    def poll(cls, context):
        scene_props = get_scene_props(context)
        item = get_scatter_item(context)
        category = scene_props.active_category
        return (
            item
            and item.get_ntree_version() >= (2, 1, 0)
            and category in ["DISTRIBUTION", "SCALE"]
        )


class SelectEffectOperator(bpy.types.Operator):
    bl_idname = "gscatter.select_effect"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_label = "Select Effect"
    bl_description = "Select Effect"

    effect_name: bpy.props.StringProperty()
    node: bpy.types.GeometryNodeGroup

    def invoke(self, context: Context, event: bpy.types.Event) -> set:
        scene_props = get_scene_props(context)
        category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]

        utils.select_effect(self.effect_name, node.node_tree)
        return {"FINISHED"}


class MoveEffectOperator(bpy.types.Operator):
    bl_idname = "gscatter.move_effect"
    bl_label = "Move Effect"
    bl_description = ""

    up: bpy.props.BoolProperty(default=True)
    effect_name: bpy.props.StringProperty()
    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context: Context, operator):
        return operator.tooltip

    def execute(self, context: bpy.types.Context) -> set:
        scene_props = get_scene_props(context)
        category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effects: bpy.types.bpy_prop_collection = node.node_tree.gscatter.effects
        effect_index = effects.find(self.effect_name)

        if effect_index + 1 == len(effects) and self.up:
            return {"CANCELLED"}
        if effect_index == 0 and not self.up:
            return {"CANCELLED"}

        utils.move_effect(self.effect_name, node.node_tree, self.up)
        return {"FINISHED"}


class DeleteEffectOperator(bpy.types.Operator):
    bl_idname = "gscatter.delete_effect"
    bl_label = "Delete Effect"
    bl_description = "Delete the selected Effect"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        scene_props = get_scene_props(context)
        category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effect: "EffectLayerProps" = node.node_tree.gscatter.get_selected()
        return True if effect else False

    def execute(self, context: Context):
        scene_props = get_scene_props(context)
        category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effect: "EffectLayerProps" = node.node_tree.gscatter.get_selected()

        utils.delete_effect(effect.name, node.node_tree)
        if scene_props.visualizing:
            if not utils.can_visualize_selected_effect(context):
                override = context.copy()
                with context.temp_override(**override):
                    bpy.ops.gscatter.visualize_off("INVOKE_DEFAULT", mode="OFF")
                self.report({"WARNING"}, message="No Effects anymore to Visualize!")
                return {"FINISHED"}
        return {"FINISHED"}


def enumerate_effects(self, context: bpy.types.Context):
    scene_props = get_scene_props(context)
    category: str = scene_props.active_category
    added_ids = []
    effect_list = []

    for effect in effectstore.get_all():
        if (
            effect.namespace == "internal"
            or effect.id in added_ids
            or category not in effect.categories
            or effect.schema_version < default.EFFECT_SCHEMA_VERSION
        ):
            continue
        added_ids.append(effect.id)
        effect_list.append(effectstore.get_newest_by_id(effect.id))

    enum: List[Tuple[str, str, str, str, int]] = []
    indices = itertools.count()

    for effect_subcategory in default.EFFECT_SUBCATEGORIES:
        try:
            first = next(indices)
        except StopIteration:
            return
        enum.append(("", effect_subcategory, "", "NONE", first))
        effects = [
            effect
            for effect in effect_list
            if effect and effect.subcategory == effect_subcategory
        ]
        effects.sort(key=lambda effect: effect.name.lower())
        for effect in effects:
            try:
                following = next(indices)
            except StopIteration:
                return
            icon = (
                icons.get(effect.icon) if icons.is_custom(effect.icon) else effect.icon
            )
            enum.append((effect.id, effect.name, effect.description, icon, following))

    return enum


class AddEffectOperator(bpy.types.Operator):
    bl_idname = "gscatter.add_effect"
    bl_label = "Add Effect"
    bl_description: str = "Add a new effect"
    bl_options = {"UNDO"}

    type: bpy.props.EnumProperty(items=enumerate_effects)

    def execute(self, context: Context):
        scene_props = get_scene_props(context)
        category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]

        effect_id = self.type
        effect_ntree = utils.get_effect_nodetree(effect_id)
        version = effectstore.get_newest_by_id(effect_id).effect_version
        utils.add_effect(effect_ntree, node.node_tree, category, effect_id, version)
        return {"FINISHED"}


class PaintWeightMapOperator(bpy.types.Operator):
    bl_idname = "gscatter.paint_weight_map"
    bl_label = "Paint Weight Map"

    effect_name: bpy.props.StringProperty()
    input_name: bpy.props.StringProperty()

    def execute(self, context: Context):
        if context.mode == "OBJECT":
            scene_props = get_scene_props(context)
            category: str = scene_props.active_category
            scatter_surface = get_scatter_surface(context)
            scatter_system = get_scatter_system(context)
            node_tree = get_node_tree(context)
            node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
            effects: bpy.types.bpy_prop_collection = node.node_tree.gscatter.effects
            weight_map_effect: "EffectLayerProps" = effects[self.effect_name]

            vg_name: str = weight_map_effect.effect_node.inputs[
                self.input_name
            ].default_value
            if vg_name == "" or scatter_surface.vertex_groups.get(vg_name) is None:
                vg = scatter_surface.vertex_groups.new()
                vg_name = vg.name
            vg = scatter_surface.vertex_groups.get(vg_name)
            scatter_surface.vertex_groups.active = vg
            weight_map_effect.effect_node.inputs[
                self.input_name
            ].default_value = vg.name

            scatter_system.hide_set(False)
            scatter_surface.hide_set(False)
            bpy.ops.object.select_all(action="DESELECT")
            scatter_surface.select_set(True)

            context.view_layer.objects.active = scatter_surface
            bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
            return {"FINISHED"}

        elif context.mode == "PAINT_WEIGHT":
            bpy.ops.object.mode_set(mode="OBJECT")
            return {"FINISHED"}

        return {"CANCELLED"}


def enum_categories(self, context: Context):
    scene_props = get_scene_props(context)
    src_cat: str = scene_props.active_category
    node_tree = get_node_tree(context)
    src_node: bpy.types.GeometryNodeGroup = node_tree.nodes[src_cat]
    src_effect: "EffectLayerProps" = src_node.node_tree.gscatter.get_selected()
    supported_categories = effectstore.get_by_id_and_version(
        src_effect.get_effect_id(), src_effect.get_effect_version()
    ).categories

    indices = itertools.count()
    category_enum = [("", "Copy to", "")]
    category_enum += [
        (
            "COPY:" + cat,
            default.EFFECT_CATEGORIES[cat],
            f"The {cat} category",
            "UNLINKED",
            next(indices),
        )
        for cat in supported_categories
    ]
    category_enum += [("", "Link to", "")]
    category_enum += [
        (
            "LINK:" + cat,
            default.EFFECT_CATEGORIES[cat],
            f"The {cat} category",
            "LINKED",
            next(indices),
        )
        for cat in supported_categories
    ]

    return category_enum


class DuplicateEffectOperator(bpy.types.Operator):
    bl_idname = "gscatter.duplicate_effect"
    bl_label = "Duplicate"
    bl_description = "Duplicate the selected Effect"
    bl_options = {"UNDO"}

    target: bpy.props.EnumProperty(name="Target Category", items=enum_categories)

    def execute(self, context: Context):
        target = self.target.split(":")[1]
        scene_props = get_scene_props(context)
        get_scatter_surface(context)
        src_cat: str = scene_props.active_category
        node_tree = get_node_tree(context)
        src_node: bpy.types.GeometryNodeGroup = node_tree.nodes[src_cat]
        src_effect: "EffectLayerProps" = src_node.node_tree.gscatter.get_selected()
        dst_node: bpy.types.GeometryNodeGroup = node_tree.nodes[target]

        if self.target.startswith("COPY:"):
            utils.duplicate_effect(dst_node.node_tree, target, src_effect)
            self.report({"INFO"}, message="Effect copied successfully")
        else:
            utils.add_effect(
                src_effect.group_node.node_tree,
                dst_node.node_tree,
                target,
                src_effect.get_effect_id(),
                src_effect.get_effect_version(),
                None,
                False,
            )
            self.report({"INFO"}, message="Effect linked successfully")

        return {"FINISHED"}


class ChangeEffectPresetOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.change_effect_preset"
    bl_label: str = "Change Effect Preset"
    bl_description: str = "Change the current preset to the selected preset"
    bl_options = {"UNDO"}

    type: bpy.props.StringProperty()

    def execute(self, context):
        scene_props = get_scene_props(context)
        category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effect: "EffectLayerProps" = node.node_tree.gscatter.get_selected()

        effect_preset = effectpresetstore.get_by_id(self.type)

        set_dropdown(effect, effect_preset.dropdowns)
        set_params(effect.effect_node, effect_preset.params)
        set_layer_params(effect, effect_preset.layer_params)
        set_node_props(effect, effect_preset.nodes, effect.get_effect_id())

        self.report({"INFO"}, message="Preset Applied")
        return {"FINISHED"}


class RemoveEffectPresetOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.remove_effect_preset"
    bl_label: str = "Remove Effect Preset"
    bl_description: str = "Remove the selected preset"
    bl_options = {"UNDO"}

    type: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: Context):
        effectpresetstore.remove(self.type)
        self.report({"INFO"}, message="Removed preset")
        return {"FINISHED"}


def clean(value: Any) -> Union[str, list, Any, None]:
    """Cleans arbitrary datatypes for conversion to string."""
    if isinstance(value, str):
        return value
    if hasattr(value, "__len__"):
        return list(value)
    if hasattr(value, "__add__"):
        return value
    return None


class AddNewPresetOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.add_new_effect_preset"
    bl_label: str = "Add Effect Preset"
    bl_description: str = "Add a new effect preset"
    bl_options = {"UNDO"}

    def execute(self, context: Context):
        wm_props = get_wm_props(context)
        scene_props = get_scene_props(context)
        if len(wm_props.new_preset.strip()) == 0:
            self.report({"INFO"}, message="A name is required. Cancelled")
            return {"CANCELLED"}

        category: str = scene_props.active_category
        node_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        effect: "EffectLayerProps" = node.node_tree.gscatter.get_selected()

        preset_id = str(uuid4())
        preset_name = wm_props.new_preset

        effect_data, dependencies = get_effect_data(effect, False, {})

        new_preset = EffectPreset(
            preset_id,
            preset_name,
            effect_data["effect_id"],
            effect_data["effect_version"],
            effect_data["params"],
            effect_data["layer_params"],
            effect_data["nodes"],
            effect_data.get("dropdowns", {}),
        )
        effectpresetstore.add("user", new_preset)
        wm_props.new_preset = "New Preset"
        self.report({"INFO"}, message="Added a new preset")
        return {"FINISHED"}


class MuteEffectOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.mute_effect"
    bl_label: str = "Mute Effect"
    bl_description: str = "Mute the selected effect"
    bl_options = {"UNDO"}

    node_name: bpy.props.StringProperty()

    def execute(self, context: Context):
        scene_props = get_scene_props(context)
        category = scene_props.active_category
        main_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = main_tree.nodes[category]

        effect_node = node.node_tree.nodes[self.node_name]
        effect_node.mute = not effect_node.mute

        if effect_node.mute:
            prev_viz_node = utils.trees.get_node_with_visualization(
                effect_node, mode="BEFORE"
            )
            next_viz_node = utils.trees.get_node_with_visualization(
                effect_node, mode="AFTER"
            )

            node.node_tree.links.new(
                input=next_viz_node.inputs["Original Geometry"],
                output=prev_viz_node.outputs["Original Geometry"],
            )
        else:
            utils.trees.connect_visualization_input_outputs(effect_node, node.node_tree)
        return {"FINISHED"}


def get_available_effects(self, context: Context):
    scene_props = get_scene_props(context)
    category: str = scene_props.active_category

    items = []
    indices = itertools.count()
    for node_group in bpy.data.node_groups:
        if (
            category in node_group.gscatter.category
            and node_group.gscatter.is_gscatter_effect
        ):
            icon = (
                icons.get(node_group.gscatter.icon)
                if icons.is_custom(node_group.gscatter.icon)
                else node_group.gscatter.icon
            )
            items.append((node_group.name, node_group.name, "", icon, next(indices)))
    return items


class AddExistingEffectOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.add_existing_effect"
    bl_label: str = "Add existing Effect"
    bl_description: str = "Select from available Effects"
    bl_options = {"UNDO"}

    type: bpy.props.EnumProperty(name="Effects", items=get_available_effects)

    def execute(self, context: Context):
        scene_props = get_scene_props(context)
        category = scene_props.active_category
        main_tree = get_node_tree(context)

        node: bpy.types.GeometryNodeGroup = main_tree.nodes[category]

        node_group = bpy.data.node_groups.get(self.type)

        utils.add_effect(
            node_group,
            node.node_tree,
            category,
            node_group.gscatter.effect_id,
            node_group.gscatter.version,
            None,
            False,
        )

        return {"FINISHED"}


class SetEffectListOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.set_effect"
    bl_label: str = "Effects"
    bl_description: str = "Select from available effects"

    node_name: bpy.props.StringProperty()
    category: bpy.props.StringProperty()

    type: bpy.props.EnumProperty(
        name="Effects",
        items=get_available_effects,
    )

    def execute(self, context: Context):
        scene_props = get_scene_props(context)
        get_scatter_surface(context)

        category = scene_props.active_category
        main_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = main_tree.nodes[category]

        effect_node = node.node_tree.nodes[self.node_name]

        node_before = effect_node.inputs[0].links[0].from_node
        node_after = effect_node.outputs[0].links[0].to_node

        node_group = bpy.data.node_groups.get(self.type)
        if node_group:
            effect_node.node_tree = node_group

        node.node_tree.links.new(
            output=node_before.outputs[0], input=effect_node.inputs[0]
        )
        node.node_tree.links.new(
            output=effect_node.outputs[0], input=node_after.inputs[0]
        )

        utils.trees.connect_visualization_input_outputs(effect_node, node.node_tree)

        effect_node.label = node_group.name

        utils.set_channel_input(effect_node, category)

        for effect in node.node_tree.gscatter.effects:
            if effect.group_node == effect_node:
                effect.influence = effect.influence
                effect.blend_type = effect.blend_type
                effect.invert = effect.invert
        return {"FINISHED"}


class MakeUniqueEffectOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.make_unique_effect"
    bl_label: str = "Make Effect Unique"
    bl_description: str = "Make selected effect unique"
    bl_options = {"UNDO"}

    node_name: bpy.props.StringProperty()
    effect_name: bpy.props.StringProperty()

    def execute(self, context: Context):
        scene_props = get_scene_props(context)
        category = scene_props.active_category
        main_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = main_tree.nodes[category]
        effect_node = node.node_tree.nodes[self.node_name]
        effect_node.node_tree = effect_node.node_tree.copy()

        effect = node.node_tree.gscatter.effects[self.effect_name]
        effect.effect_node.node_tree = effect.effect_node.node_tree.copy()
        effect.instance_id = str(uuid4())
        return {"FINISHED"}


class ToggleLayerCollapseOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.toggle_layer_collapse"
    bl_label: str = "Open/Close layer"
    bl_description: str = "\u2022 Shift to affect all layers.\n\u2022 Ctrl to affect all layers except for this layer"

    all_except_current: bpy.props.BoolProperty(default=False)
    all: bpy.props.BoolProperty(default=False)
    effect_name: bpy.props.StringProperty()

    def invoke(self, context: Context, event):
        if event.ctrl:
            self.all_except_current = True
        elif event.shift:
            self.all = True
        return self.execute(context)

    def execute(self, context: Context):
        scene_props = get_scene_props(context)
        category = scene_props.active_category
        main_tree = get_node_tree(context)
        node: bpy.types.GeometryNodeGroup = main_tree.nodes[category]

        effects: list["EffectLayerProps"] = node.node_tree.gscatter.effects
        cur_effect: "EffectLayerProps" = effects[self.effect_name]
        if self.all_except_current:
            for effect in effects:
                if effect.name != self.effect_name:
                    effect.open = not effect.open
        elif self.all:
            cur_effect.open = not cur_effect.open
            for effect in effects:
                effect.open = cur_effect.open
        else:
            cur_effect.open = not cur_effect.open
        return {"FINISHED"}


class AddEffectInputToEffectPropertiesOperator(bpy.types.Operator):
    bl_idname = "gscatter.set_input_as_env_property"
    bl_options = {"UNDO"}
    bl_label = "Add Environment Property"
    bl_description = "Add this Input as a new environment property"

    effect: bpy.props.StringProperty()
    effect_instance_id: bpy.props.StringProperty()
    input: bpy.props.StringProperty()
    input_idx: bpy.props.IntProperty()
    input_label: bpy.props.StringProperty()

    tooltip: bpy.props.StringProperty()

    new_label: bpy.props.StringProperty(name="Name")

    def draw(self, context: Context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "new_label")

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        self.new_label = self.input_label
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        env_props = ss.gscatter.environment_props.props
        new_prop_entry = env_props.add()
        new_prop_entry.label = self.new_label
        new_prop_entry.effect_instance_id = self.effect_instance_id
        new_prop_entry.input = self.input
        new_prop_entry.input_idx = self.input_idx
        new_prop_entry.order_idx = len(ss.gscatter.environment_props.props) - 1
        self.report({"INFO"}, message="Property Added.")
        return {"FINISHED"}


class RenameEnvironmentPropertyOperator(bpy.types.Operator):
    bl_idname = "gscatter.rename_env_property_from_input"
    bl_options = {"UNDO"}
    bl_label = "Rename Environment Property"
    bl_description = "Rename the environment property of this Input"

    input: bpy.props.StringProperty()
    input_label: bpy.props.StringProperty()

    tooltip: bpy.props.StringProperty()

    new_label: bpy.props.StringProperty(name="Name")

    def draw(self, context: Context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "new_label")

    def invoke(self, context: Context, event: bpy.types.Event):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        env_props = ss.gscatter.environment_props.props
        target_prop = False
        for prop in env_props:
            if prop.input == self.input:
                target_prop = prop
                break
        # Just renaming
        if target_prop:
            self.new_label = target_prop.label
            return context.window_manager.invoke_props_dialog(self)
        return {"CANCELLED"}

    def execute(self, context: Context):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        env_props = ss.gscatter.environment_props.props
        target_prop = False
        for prop in env_props:
            if prop.input == self.input:
                target_prop = prop
                break
        # Just renaming
        if target_prop:
            target_prop.label = self.new_label
            self.report({"INFO"}, message="Property Renamed.")

        return {"FINISHED"}


classes = (
    SelectEffectOperator,
    DeleteEffectOperator,
    MoveEffectOperator,
    AddEffectOperator,
    DuplicateEffectOperator,
    ChangeEffectPresetOperator,
    RemoveEffectPresetOperator,
    AddNewPresetOperator,
    VisualizeOffOperator,
    VisualizeSelectedEffectOperator,
    VisualizeAllEffectOperator,
    MuteEffectOperator,
    SetEffectListOperator,
    MakeUniqueEffectOperator,
    AddExistingEffectOperator,
    PaintWeightMapOperator,
    ToggleLayerCollapseOperator,
    AddEffectInputToEffectPropertiesOperator,
    RenameEnvironmentPropertyOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
