from random import random
from typing import TYPE_CHECKING, Any, Union
from uuid import uuid4

import bpy

from ..utils.logger import debug

from .. import effects
from ..asset_manager.asset_browser import open_asset_browser
from ..common.props import ScatterItemProps, SceneProps
from ..effects import utils
from ..effects.props import EffectLayerProps
from ..effects.utils.setter import set_effect_properties
from ..effects.utils.trees import deepcopy_nodetree
from ..environment.utils import add_environment
from ..utils import main_collection
from ..utils.getters import (
    get_scene_props,
    get_node_tree,
    get_preferences,
    get_scatter_surface,
    get_scatter_props,
    get_wm_props,
    get_instance_col,
    get_system_tree,
    get_nodes_modifier,
    get_scatter_system,
    get_scatter_system_effects,
    get_scatter_item,
)
from . import default
from .functions import (
    create_main_tree,
    create_scatter_node_trees,
    scatter_collection,
    scatter_objects,
)
from .store import scattersystempresetstore
from .store.scatter_system_preset_item import ScatterSystemPreset
from .utils import get_selected_asset, get_asset_browser, get_available_systems

if TYPE_CHECKING:
    from ..asset_manager.props.library import LibraryWidget

NON_PRIMITIVE_SOCKETS = {
    "NodeSocketGeometry",
    "NodeSocketMaterial",
    "NodeSocketTexture",
}


def clean(value: Any) -> Union[str, list, Any, None]:
    """Cleans arbitrary datatypes for conversion to string."""
    if isinstance(value, str):
        return value
    if hasattr(value, "__len__"):
        return list(value)
    if hasattr(value, "__add__"):
        return value
    return None


def recursively_delete_effect_groups(node_tree, materials=None):
    # Delete all the nodes within the group
    if hasattr(node_tree, "nodes"):
        # debug(f"Deleting node group: {node_tree.name}")
        if node_tree.users < 2:
            for child_node in node_tree.nodes:
                if hasattr(child_node, "node_tree"):
                    recursively_delete_effect_groups(child_node.node_tree)
            bpy.data.node_groups.remove(node_tree)

    # Remove the group from any material or shader it's used in
    if materials is not None:
        for material in materials:
            if material.use_nodes:
                for child_node in material.node_tree.nodes:
                    if hasattr(child_node, "node_tree"):
                        recursively_delete_effect_groups(child_node.node_tree)


class ScatterSelectedToActive(bpy.types.Operator):
    bl_idname = "gscatter.scatter_selected_to_active"
    bl_label = "Scatter Selected on Active"
    bl_description = "Scatter selected objects onto the active object \n\u2022 Cltr and click to Scatter Individually"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    individual: bpy.props.BoolProperty(
        name="Scatter Individually",
        description="Create a scatter system for each selected object",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        scene_props = get_scene_props(context)
        active_object = context.active_object
        selected_objects = context.selected_objects

        asset_area = get_asset_browser(context)
        if asset_area:
            with bpy.context.temp_override(area=asset_area):
                c = bpy.context
                selection = []
                try:
                    if c.selected_asset_files:
                        selection = c.selected_asset_files
                        if len(selection) > 0:
                            if context.active_object:
                                return True
                except AttributeError:
                    if c.selected_assets:
                        selection = c.selected_assets
                        if len(selection) > 0:
                            if context.active_object:
                                return True

        if (
            active_object is not None
            and active_object.type == "MESH"
            and context.mode == "OBJECT"
            and active_object.select_get()
        ):
            if len(selected_objects) > 1:
                selected_objects.remove(active_object)
                if scene_props.scatter_surface not in selected_objects:
                    return True
        return False

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set:
        if event.ctrl:
            self.individual = True

        active_object = context.active_object
        selected_objects = context.selected_objects
        selected_objects.remove(active_object)

        if active_object.gscatter.is_gscatter_system:
            self.report({"WARNING"}, "Active Object is a scatter system")
        if any(get_node_tree(object) for object in selected_objects):
            self.report({"WARNING"}, "Scattering existing system")

        return self.execute(context)

    def execute(self, context):
        scene_props = get_scene_props(context)
        active_object = context.active_object
        selected_objects = context.selected_objects
        selected_objects.remove(active_object)

        scene_props.scatter_surface = active_object
        scene_props.use_active_object_as_scatter_surface = False
        active_object.select_set(False)

        override = context.copy()
        override["selected_objects"] = list(selected_objects)
        with context.temp_override(**override):
            bpy.ops.gscatter.scatter(individual=self.individual)
        return {"FINISHED"}


class ScatterOperator(bpy.types.Operator):
    """Scatters one or more objects or assets across the surface.\n\u2022 Ctrl and click to scatter individually"""

    bl_idname = "gscatter.scatter"
    bl_label = "Scatter Selected"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    preset: bpy.props.StringProperty(name="Preset", default="system.default")
    individual: bpy.props.BoolProperty(
        name="Scatter Individually",
        description="Create a scatter system for each selected object",
        default=False,
    )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        scene_props = get_scene_props(context)
        selected_objects = context.selected_objects

        asset_area = get_asset_browser(context)
        if asset_area:
            with bpy.context.temp_override(area=asset_area):
                c = bpy.context
                try:
                    if c.selected_asset_files:
                        return True
                except AttributeError:
                    if c.selected_assets:
                        return True

        if selected_objects:
            if scene_props.scatter_surface in selected_objects:
                return False
            return True
        return False

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set:
        if event.ctrl:
            self.individual = True

        asset_area = get_asset_browser(context)
        if asset_area:
            with bpy.context.temp_override(area=asset_area):
                c = bpy.context
                selection = []
                try:
                    if c.selected_asset_files:
                        selection = c.selected_asset_files
                except AttributeError:
                    if c.selected_assets:
                        selection = c.selected_assets
                if not len(selection) != 0 and not context.selected_objects:
                    self.report(
                        {"ERROR_INVALID_INPUT"},
                        "No selected assets in asset browser to scatter",
                    )
                    return {"CANCELLED"}
        else:
            if not context.selected_objects:
                self.report({"ERROR_INVALID_INPUT"}, "No selected objects to scatter")
                return {"CANCELLED"}

            if any(get_node_tree(object) for object in context.selected_objects):
                self.report({"WARNING"}, "Scattering existing system")

            if get_scatter_surface(context).select_get():
                self.report({"WARNING"}, "Scattering object onto itself")
        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set:
        prefs = get_preferences()
        self.preset = prefs.default_scatter_preset
        asset_area = get_asset_browser(context)
        if asset_area:
            with bpy.context.temp_override(area=asset_area):
                c = bpy.context
                selection = []
                try:
                    if c.selected_asset_files:
                        selection = c.selected_asset_files
                except AttributeError:
                    if c.selected_assets:
                        selection = c.selected_assets
                if len(selection) > 0:
                    cols = get_selected_asset(asset_area)
                    if len(cols) == 0:
                        debug(f"collections identified: {len(cols)}")
                        return {"CANCELLED"}
                    for col in cols:
                        debug(col.name)
                        if self.individual:
                            debug("indivual")
                            scatter_objects(
                                [obj for obj in col.objects],
                                self.individual,
                                self.preset,
                            )
                        else:
                            scatter_collection(col, self.preset)

                else:
                    scatter_objects(
                        context.selected_objects, self.individual, self.preset
                    )
        else:
            scatter_objects(context.selected_objects, self.individual, self.preset)

        message = "Individual" if self.individual else "Together"
        self.report({"INFO"}, message=f"Scatter Selected {message}")
        return {"FINISHED"}


class DeleteScatterItemOperator(bpy.types.Operator):
    """Delete the selected item from the list"""

    bl_idname = "gscatter.delete_scatter_item"
    bl_label = "Deletes a scatter item"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        scatter_props = get_scatter_props(context)
        items: list[ScatterItemProps] = scatter_props.scatter_items
        index: int = scatter_props.scatter_index
        return index in range(len(items))

    def execute(self, context: bpy.types.Context) -> set:
        scene_props = get_scene_props(context)
        scatter_props = get_scatter_props(context)
        items: list[ScatterItemProps] = scatter_props.scatter_items
        index: int = scatter_props.scatter_index
        item_obj: bpy.context.object = items[index].obj
        col = get_instance_col(item_obj)
        is_gscatter_asset = col.gscatter.is_gscatter_asset if col is not None else False
        proxy_mat = bpy.data.materials.get("proxy_" + item_obj.name)
        if proxy_mat:
            bpy.data.materials.remove(proxy_mat)

        main_tree = get_system_tree(item_obj)

        if main_tree:
            object_node = main_tree.nodes.get(scene_props.scatter_surface.name)
            if object_node is not None:
                main_tree.nodes.remove(object_node)

            if len(main_tree.nodes["Join Geometry"].inputs[0].links) == 0:
                gscatter_node_tree = get_node_tree(
                    item_obj
                )  # main_tree.nodes["GScatter"].node_tree
                if gscatter_node_tree.users == 1:
                    is_old = tuple(items[index].ntree_version) < (2, 1, 0)
                    (
                        distribution,
                        scale,
                        rotation,
                        geometry,
                        _,
                        dependencies,
                    ) = get_scatter_system_effects(item_obj, is_old)

                    for effect_data in distribution + scale + rotation + geometry:
                        effect = bpy.data.node_groups[effect_data["name"]]
                        if effect.users < 2:
                            recursively_delete_effect_groups(
                                effect, dependencies["materials"]
                            )

                recursively_delete_effect_groups(gscatter_node_tree)
            recursively_delete_effect_groups(main_tree)

        for group in bpy.data.node_groups:
            if group.users == 0 and group.gscatter.is_gscatter_effect:
                recursively_delete_effect_groups(group)

        viz_copy_name = item_obj.name + "_viz_copy"
        viz_copy_tree = bpy.data.node_groups.get(viz_copy_name)
        if viz_copy_tree:
            bpy.data.node_groups.remove(viz_copy_tree)

        for child_col in item_obj.users_collection:  # bpy.data.collections.values():
            # if col.name.startswith("Systems"):
            # for child_col in bpy.data.collections.values():
            if child_col.name.startswith(f"{item_obj.name}"):
                bpy.data.collections.remove(child_col)

        bpy.data.objects.remove(item_obj)
        items.remove(index)
        scatter_props.scatter_index = index if len(items) > index else index - 1

        if col:
            # Check if other system has the same source
            has_same_source = False

            for obj in context.view_layer.objects:
                if obj and obj != item_obj:
                    for item in obj.gscatter.scatter_items:
                        if get_instance_col(item.obj) == col:
                            has_same_source = True
                            break

            # If no system uses the source, check if it's an asset from gscatter
            if not has_same_source:
                if is_gscatter_asset:
                    for obj in col.objects:
                        bpy.data.objects.remove(obj)
                    bpy.data.collections.remove(col)
                else:
                    if col.library:
                        bpy.data.collections.remove(col)
                    else:
                        for obj in col.objects:
                            col.objects.unlink(obj)
                            if not obj.users_collection:
                                if obj.gscatter.is_gscatter_system:
                                    col_sources = main_collection(sub="Systems")
                                    col_sources.objects.link(obj)
                                else:
                                    context.view_layer.layer_collection.collection.objects.link(
                                        obj
                                    )
                    bpy.data.collections.remove(col)

        self.report({"INFO"}, "Deleted Scatter System")
        return {"FINISHED"}


class ToggleProxyOperator(bpy.types.Operator):
    """\u2022 Ctrl to affect all except this item.\n\u2022 Shift to affect all"""

    bl_idname = "gscatter.toggle_scatter_item"
    bl_label = "Toggle scatter item proxy display"
    bl_options = {"UNDO", "INTERNAL"}

    index: bpy.props.IntProperty()
    all_except_current: bpy.props.BoolProperty(default=False)
    all: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.all_except_current = True
        elif event.shift:
            self.all = True

        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set:
        scatter_props = get_scatter_props(context)
        items: list[ScatterItemProps] = scatter_props.scatter_items
        scatter_item: ScatterItemProps = items[self.index]
        obj = scatter_item.obj

        if self.all_except_current:
            for item in items:
                if item.obj != obj:
                    viewport_proxy = not item.viewport_proxy
                    item.viewport_proxy = viewport_proxy
        elif self.all:
            viewport_proxy = not scatter_item.viewport_proxy
            for item in items:
                item.viewport_proxy = viewport_proxy

        else:
            viewport_proxy = not scatter_item.viewport_proxy
            scatter_item.viewport_proxy = viewport_proxy
        return {"FINISHED"}


class ToggleVisibilityOperator(bpy.types.Operator):
    """\u2022 Ctrl to affect all except this item.\n\u2022 Shift to affect all"""

    bl_idname = "gscatter.toggle_scatter_item_visibility"
    bl_label = "Toggle scatter item visibility"
    bl_options = {"UNDO", "INTERNAL"}

    index: bpy.props.IntProperty()
    all_except_current: bpy.props.BoolProperty(default=False)
    all: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.all_except_current = True
        elif event.shift:
            self.all = True

        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set:
        scatter_props = get_scatter_props(context)
        items: list[ScatterItemProps] = scatter_props.scatter_items
        scatter_item: ScatterItemProps = items[self.index]
        obj = scatter_item.obj

        if self.all_except_current:
            for item in items:
                if item.obj != obj:
                    visibility = item.obj.visible_get()
                    item.obj.hide_set(visibility)
                    item.obj.hide_viewport = visibility
        elif self.all:
            visible = not obj.visible_get()
            for item in items:
                item.obj.hide_set(not visible)
                item.obj.hide_viewport = not visible

        else:
            visible = obj.visible_get()
            obj.hide_set(visible)
            obj.hide_viewport = visible
        return {"FINISHED"}


class MoveScatterItemOperator(bpy.types.Operator):
    """Move an item in the list"""

    bl_idname = "gscatter.move_scatter_item"
    bl_label = "Move an item in the list"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    direction: bpy.props.EnumProperty(
        items=(
            ("UP", "Up", ""),
            ("DOWN", "Down", ""),
        )
    )

    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, operator):
        return operator.tooltip

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        scatter_props = get_scatter_props(context)
        items: list[ScatterItemProps] = scatter_props.scatter_items
        index: int = scatter_props.scatter_index
        return len(items) > 1 and index in range(len(items))

    def move_index(self, context: bpy.types.Context):
        """Move index of an item render queue while clamping it."""
        scatter_props = get_scatter_props(context)
        index = scatter_props.scatter_index
        list_length = len(scatter_props.scatter_items) - 1
        new_index = index + (-1 if self.direction == "UP" else 1)
        scatter_props.scatter_index = max(0, min(new_index, list_length))

    def execute(self, context: bpy.types.Context) -> set:
        scatter_props = get_scatter_props(context)
        items: list[ScatterItemProps] = scatter_props.scatter_items
        index: int = scatter_props.scatter_index
        neighbor = index + (-1 if self.direction == "UP" else 1)
        items.move(neighbor, index)
        self.move_index(context)
        return {"FINISHED"}


class DuplicateScatterItemOperator(bpy.types.Operator):
    """Duplicate an item in the list. Makes a deep copy"""

    bl_idname = "gscatter.duplicate_scatter_item"
    bl_label = "Duplicate scatter item"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        scatter_props = get_scatter_props(context)
        items: list[ScatterItemProps] = scatter_props.scatter_items
        index: int = scatter_props.scatter_index
        return index in range(len(items))

    def execute(self, context: bpy.types.Context) -> set:
        scene_props = get_scene_props(context)
        system_old = get_scatter_system(context)
        system_new: bpy.types.Object = system_old.copy()
        system_new.data = system_old.data.copy()

        for collection in system_old.users_collection:
            if collection not in system_new.users_collection:
                collection.objects.link(system_new)

        node_tree_old = get_node_tree(system_old)
        node_tree_new = deepcopy_nodetree(node_tree_old)
        grp = create_main_tree(scene_props.scatter_surface, node_tree_new)

        modifier_new = get_nodes_modifier(system_new)
        modifier_new.node_group = grp

        color = (random(), random(), random(), 1)
        system_new.color = color
        proxy_mat = bpy.data.materials.new(name=f"proxy_{system_new.name}")
        proxy_mat.diffuse_color = color

        scatter_props = get_scatter_props(context)
        item_new = scatter_props.scatter_items.add()
        item_new.name = system_new.name
        item_new.obj = system_new
        item_new.color = color
        item_new.proxy_mat = proxy_mat
        item_new.ntree_version = default.NODETREE_VERSION

        node_tree_new.nodes["VIEWPORT_PROXY"].node_tree.nodes["proxy_material"].inputs[
            2
        ].default_value = proxy_mat

        scatter_props.scatter_index = len(scatter_props.scatter_items) - 1

        return {"FINISHED"}


class ClosePopupOperator(bpy.types.Operator):
    """Closes a popup"""

    bl_idname: str = "gscatter.close_popup"
    bl_label: str = "Cancel"
    bl_description: str = "Closes a popup"

    def execute(self, context):
        bpy.context.window.screen = bpy.context.window.screen
        return {"FINISHED"}


class UpdateScatterSystemTreeOperator(bpy.types.Operator):
    """Update scatter system main node tree"""

    bl_idname = "gscatter.update_scatter_system_tree"
    bl_label = "GScatter Update Scatter System"

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("ALL", "All", "Update all system", "", 0),
            ("SINGLE", "Single", "Update one system", "", 1),
        ],
    )
    system_index: bpy.props.IntProperty(name="Scatter system index", default=0)
    update: bpy.props.BoolProperty(name="Update", default=False)

    def draw(self, context):
        layout = self.layout
        scatter_props = get_scatter_props(context)

        layout.label(text="GScatter old system detected.", icon="ERROR")

        if self.mode == "ALL":
            text = "This file contains an older version of Scatter System. \nWould you like to update to the newest version?"
        else:
            scatter_system = scatter_props.scatter_items[self.system_index]
            text = f"{scatter_system.obj.name} is using old node tree. \nWould you like to update to the newest version?"
        col = layout.column()
        col.scale_y = 0.7
        for line in text.splitlines():
            col.label(text=line)
        col.separator()

    def invoke(self, context, event):
        if self.update:
            self.update = False
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self)

    def set_effect_props(
        self,
        scatter_system,
        distribution,
        scale,
        rotation,
        geometry,
        effect_trees: dict,
    ):
        collection = get_instance_col(scatter_system.obj)
        node_tree = get_node_tree(scatter_system.obj)
        proxy_mat = bpy.data.materials.get("proxy_" + scatter_system.obj.name)
        if proxy_mat is None:
            color = (random(), random(), random(), 1)
            proxy_mat = bpy.data.materials.new(name=f"proxy_{scatter_system.obj.name}")
            proxy_mat.diffuse_color = color
        scatter_system.color = proxy_mat.diffuse_color
        scatter_system.obj.color = proxy_mat.diffuse_color

        node_tree.nodes.clear()
        scatter_system.ntree_version = default.NODETREE_VERSION

        m: bpy.types.NodesModifier = get_nodes_modifier(scatter_system.obj)
        main_ntree = create_scatter_node_trees(
            bpy.context.scene.gscatter.scatter_surface, scatter_system
        )
        m.node_group = main_ntree
        gscatter_tree = get_node_tree(scatter_system.obj)
        gscatter_tree.nodes["VIEWPORT_PROXY"].node_tree.nodes["proxy_material"].inputs[
            2
        ].default_value = proxy_mat
        scatter_system.proxy_mat = proxy_mat
        main_nodes = ["DISTRIBUTION", "SCALE", "ROTATION", "GEOMETRY"]
        for main_node in main_nodes:
            m_node: bpy.types.GeometryNodeGroup = gscatter_tree.nodes[main_node]
            ntree: bpy.types.GeometryNodeTree = m_node.node_tree
            effect_datas = (
                distribution
                if main_node == "DISTRIBUTION"
                else scale
                if main_node == "SCALE"
                else rotation
                if main_node == "ROTATION"
                else geometry
            )

            set_effect_properties(
                effect_datas, ntree, main_node, effect_trees, collection=collection
            )

    def execute(self, context):
        scatter_props = get_scatter_props(context)
        scene_props = get_scene_props(context)
        effect_trees = dict()
        if self.mode == "SINGLE":
            scatter_system: ScatterItemProps = scatter_props.scatter_items[
                self.system_index
            ]
            is_old = tuple(scatter_system.ntree_version) < (2, 1, 0)
            distribution, scale, rotation, geometry, _, _ = get_scatter_system_effects(
                scatter_system.obj, is_old
            )
            self.set_effect_props(
                scatter_system, distribution, scale, rotation, geometry, effect_trees
            )
            gscatter_tree = get_node_tree(scatter_system.obj)
            gscatter_tree.name = scatter_system.obj.name
            scatter_system.obj.gscatter.is_gscatter_system = True
        else:
            for ob in bpy.data.objects:
                for item in ob.gscatter.scatter_items:
                    is_old = tuple(item.ntree_version) < (2, 1, 0)
                    (
                        distribution,
                        scale,
                        rotation,
                        geometry,
                        _,
                        _,
                    ) = get_scatter_system_effects(item.obj, is_old)
                    self.set_effect_props(
                        item, distribution, scale, rotation, geometry, effect_trees
                    )
                    gscatter_tree = get_node_tree(item.obj)
                    gscatter_tree.name = item.obj.name
                    item.obj.gscatter.is_gscatter_system = True

        context.view_layer.objects.active = scene_props.scatter_surface
        scene_props.scatter_surface.select_set(True)

        bpy.context.window.screen = bpy.context.window.screen
        self.report({"INFO"}, message="Updated to the newest version.")
        return {"FINISHED"}


class AddNewSystemPresetOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.add_new_system_preset"
    bl_label: str = "Add Scatter System Preset"
    bl_description: str = "Add a new scatter system preset"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return get_scatter_system(context) is not None

    def execute(self, context):
        wm_props = get_wm_props(context)
        if len(wm_props.new_preset.strip()) == 0:
            self.report({"INFO"}, message="A name is required. Cancelled")
            return {"CANCELLED"}
        preset_id = str(uuid4())
        preset_name = wm_props.new_preset
        distribution, scale, rotation, geometry, _, _ = get_scatter_system_effects(
            context, False
        )
        scatter_item = get_scatter_item(context)
        new_preset = ScatterSystemPreset(
            preset_id,
            preset_name,
            scatter_item.is_terrain,
            distribution,
            scale,
            rotation,
            geometry,
        )
        scattersystempresetstore.add("user", new_preset)

        wm_props.new_preset = "New Preset"
        self.report({"INFO"}, message="Added a new preset")
        return {"FINISHED"}


class RemovePresetOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.remove_scatter_system_preset"
    bl_label: str = "Remove Scatter System Preset"
    bl_description: str = "Remove the selected preset"
    bl_options = {"UNDO"}

    type: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scattersystempresetstore.remove(self.type)
        self.report({"INFO"}, message="Removed preset")
        return {"FINISHED"}


class ChangePresetOperator(bpy.types.Operator):
    """Change the current system to the selected preset. (!Discards all Effects!)\n\u2022 Shift-click to scatter selected objects using this preset. \n\u2022 Ctrl-click to scatter selected objects indiviually using this preset."""

    bl_idname: str = "gscatter.change_scatter_system_preset"
    bl_label: str = "Change Scatter System Preset"
    # bl_description: str = "Change the current preset to the selected preset"

    type: bpy.props.StringProperty()

    individual: bpy.props.BoolProperty()
    new: bpy.props.BoolProperty()

    def invoke(self, context, event) -> set[str]:
        self.individual = event.ctrl
        self.new = event.shift
        return self.execute(context)

    def execute(self, context):
        scene_props = get_scene_props(context)
        system = get_scatter_system(context)
        if system is None or self.new:
            objs = [
                obj
                for obj in context.selected_objects
                if obj != scene_props.scatter_surface
            ]
            if objs:
                scatter_objects(objs, self.individual, self.type)
            else:
                scatter_collection(None, self.type)
            bpy.context.window.screen = bpy.context.window.screen
            self.report({"INFO"}, message="Created system successfully")
            return {"FINISHED"}

        categories = effects.default.EFFECT_CATEGORIES
        node_tree = get_node_tree(system)
        preset = scattersystempresetstore.get_by_id(self.type)
        collection = get_instance_col(system)
        warn_effects_missing = None
        effect_trees = dict()
        for main_node in categories:
            node: bpy.types.GeometryNodeGroup = node_tree.nodes[main_node]

            while node.node_tree.gscatter.get_selected():
                effect: "EffectLayerProps" = node.node_tree.gscatter.get_selected()
                utils.delete_effect(effect_name=effect.name, node_tree=node.node_tree)

            m_node: bpy.types.GeometryNodeGroup = node_tree.nodes[main_node]
            ntree: bpy.types.GeometryNodeTree = m_node.node_tree
            effect_datas = (
                preset.distribution
                if main_node == "DISTRIBUTION"
                else preset.scale
                if main_node == "SCALE"
                else preset.rotation
                if main_node == "ROTATION"
                else preset.geometry
            )
            effects_missing = set_effect_properties(
                effect_datas,
                ntree,
                main_node,
                effect_trees,
                collection=collection,
                new_instance=True,
            )
            if warn_effects_missing is None:
                warn_effects_missing = effects_missing

        if warn_effects_missing:
            self.report(
                {"ERROR"},
                message="Some effects are missing, added system may not work properly.",
            )
        else:
            self.report({"INFO"}, message="Preset Applied")

        return {"FINISHED"}


class MakeUniqueSystemOperator(bpy.types.Operator):
    """Make selected system unique \nCreates a new Scatter Object and links all effects \n\u2022 Ctrl to make all effects unique"""

    bl_idname: str = "gscatter.make_unique_system"
    bl_label: str = "Make System Unique"
    bl_options = {"UNDO", "INTERNAL"}

    make_unique_effects: bpy.props.BoolProperty(
        name="Make effect unique",
        description="Make each effect unique as well",
        default=False,
    )

    group_name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def invoke(self, context, event):
        self.make_unique_effects = False
        if event.ctrl:
            self.make_unique_effects = True
        return self.execute(context)

    def execute(self, context):
        col_systems = main_collection(sub="Systems")
        main_tree = get_system_tree(context)
        scatter = get_scatter_props(context)
        scatter_item = scatter.scatter_items[self.index]
        scene_props = get_scene_props(context)

        # Create New object to be our new Scatter System
        name = scatter_item.obj.name
        o = bpy.data.objects.new(name=name, object_data=bpy.data.meshes.new(name))
        col_systems.objects.link(o)
        # context.view_layer
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        context.view_layer.objects.active = o

        o.color = scatter_item.color
        o.display_type = (
            "BOUNDS"
            if scene_props.proxy_settings.proxy_method
            == scene_props.proxy_settings.BOUNDS
            and scatter_item.viewport_proxy
            else "TEXTURED"
        )

        scatter_item.obj = o
        scatter_item.name = o.name

        # Add an empty GeometryNodes modifier
        m: bpy.types.NodesModifier = o.modifiers.new(
            type="NODES", name="GScatterGeometryNodes"
        )

        # And copy it to the new object
        main_tree_new = main_tree.copy()
        m.node_group = main_tree_new
        o.gscatter.is_gscatter_system = True

        system_node = m.node_group.nodes["GScatter"]

        new_group: bpy.types.GeometryNodeTree = m.node_group.nodes[
            "GScatter"
        ].node_tree.copy()
        system_node.node_tree = new_group

        ## Clean-up Nodes
        main_tree.nodes.remove(main_tree.nodes[scene_props.scatter_surface.name])

        # Remove all Object links to other
        for link in main_tree_new.nodes["Join Geometry"].inputs[0].links:
            link: bpy.types.NodeLink
            main_tree_new.nodes.remove(link.from_node)

        # Re-add single Object link
        input = main_tree_new.nodes.new("GeometryNodeObjectInfo")
        input.inputs[0].default_value = scene_props.scatter_surface
        input.location = (
            0,
            len(main_tree_new.nodes["Join Geometry"].inputs[0].links) * -200,
        )
        input.name = scene_props.scatter_surface.name
        input.transform_space = "RELATIVE"
        main_tree_new.links.new(
            output=input.outputs["Geometry"],
            input=main_tree_new.nodes["Join Geometry"].inputs[0],
        )
        # Copy Effect nodegroups
        for category in effects.default.EFFECT_CATEGORIES:
            category_node = new_group.nodes[category]
            category_node.node_tree = category_node.node_tree.copy()
            debug(f"GScatter: Category Nodegroup\n {category_node.label}")

            # Make unique effects
            if self.make_unique_effects:
                # for effect in system_node.node_tree.nodes[category].node_tree.gscatter.effects:
                for effect in category_node.node_tree.gscatter.effects:
                    debug(f"Effect Nodegroup \n{effect.name}_group")

                    # Copy the group node of the effect
                    group_node = category_node.node_tree.nodes.get(
                        effect.name + "_group"
                    )
                    group_node.node_tree = group_node.node_tree.copy()

                    # Copy the inner effect node group, by getting the node from the property
                    effect = category_node.node_tree.gscatter.effects[effect.name]
                    effect.effect_node.node_tree = effect.effect_node.node_tree.copy()
                    effect.instance_id = str(uuid4())

        return {"FINISHED"}


class SetSystemListOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.set_system"
    bl_label: str = "Systems"
    bl_description: str = "Select from available systems"

    type: bpy.props.EnumProperty(
        name="Systems",
        items=get_available_systems,
    )

    index: bpy.props.IntProperty()

    def execute(self, context):
        scene_props = get_scene_props(context)
        sys_obj = bpy.data.objects.get(self.type)
        main_tree = get_system_tree(sys_obj)

        if main_tree.nodes.get(scene_props.scatter_surface.name) is None:
            scatter = get_scatter_props(context)
            scatter_item = scatter.scatter_items[self.index]

            old_tree = get_system_tree(scatter_item.obj)
            if old_tree.users == 1:
                bpy.data.objects.remove(scatter_item.obj)

            scatter_item.obj = sys_obj
            scatter_item.name = sys_obj.name
            scatter_item.color = sys_obj.color

            input = main_tree.nodes.new("GeometryNodeObjectInfo")
            input.inputs[0].default_value = scene_props.scatter_surface
            input.location = (
                0,
                len(main_tree.nodes["Join Geometry"].inputs[0].links) * -200,
            )
            input.name = scene_props.scatter_surface.name
            input.transform_space = "RELATIVE"
            main_tree.links.new(
                output=input.outputs["Geometry"],
                input=main_tree.nodes["Join Geometry"].inputs[0],
            )
        else:
            self.report({"WARNING"}, message="System is already linked. Cancelled.")
        return {"FINISHED"}


class CreateLinkedSystemOperator(bpy.types.Operator):
    bl_idname: str = "gscatter.create_linked_system"
    bl_label: str = "New Linked System"
    bl_description: str = "Select from available systems to create a linked system"
    bl_options = {"UNDO"}

    type: bpy.props.EnumProperty(
        name="Systems",
        items=get_available_systems,
    )

    def execute(self, context):
        scene_props = get_scene_props(context)
        main_collection(sub="Systems")

        sys_obj = bpy.data.objects.get(self.type)

        main_tree = get_system_tree(sys_obj)

        if main_tree.nodes.get(scene_props.scatter_surface.name) is None:
            G: SceneProps = bpy.context.scene.gscatter
            ss: bpy.types.Object = G.scatter_surface
            (random(), random(), random(), 1)
            proxy_mat = bpy.data.materials.new(name=f"proxy_{sys_obj.name}")
            proxy_mat.diffuse_color = sys_obj.color

            si_entry: ScatterItemProps = ss.gscatter.scatter_items.add()
            si_entry.obj = sys_obj
            si_entry.name = sys_obj.name
            si_entry.color = sys_obj.color
            si_entry.proxy_mat = proxy_mat
            si_entry.ntree_version = default.NODETREE_VERSION

            ss.gscatter.scatter_index = len(ss.gscatter.scatter_items) - 1

            input = main_tree.nodes.new("GeometryNodeObjectInfo")
            input.inputs[0].default_value = scene_props.scatter_surface
            input.location = (
                0,
                len(main_tree.nodes["Join Geometry"].inputs[0].links) * -200,
            )
            input.name = scene_props.scatter_surface.name
            input.transform_space = "RELATIVE"
            main_tree.links.new(
                output=input.outputs["Geometry"],
                input=main_tree.nodes["Join Geometry"].inputs[0],
            )
        else:
            self.report({"WARNING"}, message="System is already linked. Cancelled.")

        return {"FINISHED"}


class CreateEnvionmentFromTemplateOperator(bpy.types.Operator):
    bl_idname = "gscatter.create_environment_from_template"
    bl_label = "Create Environment"
    bl_description = "Create a new environment"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        wm_props = get_wm_props(context)
        starter_props = wm_props.scatter_starter
        if (
            starter_props.terrain_type == "CUSTOM"
            and starter_props.custom_terrain is None
        ):
            return False
        return True

    def execute(self, context):
        wm_props = get_wm_props(context)
        starter_props = wm_props.scatter_starter

        library: "LibraryWidget" = context.window_manager.gscatter.library
        environment_id = library.environment_enums
        environment = next(
            env for env in library.environments if env.asset_id == environment_id
        )
        effect_trees = dict()

        add_environment(context, environment, effect_trees)
        starter_props.use_environment_template = False
        return {"FINISHED"}


class DummyOperator(bpy.types.Operator):
    bl_idname = "gscatter.dummy_op"
    bl_label = "Dummy Operator"
    bl_description = "Does nothing when pressed"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> set:
        return {"CANCELLED"}


class BackOperator(bpy.types.Operator):
    bl_idname = "gscatter.back_to_start"
    bl_label = "Back"
    bl_description = "back to start"

    def execute(self, context: bpy.types.Context) -> set:
        wm_props = get_wm_props(context)
        starter_props = wm_props.scatter_starter
        starter_props.use_environment_template = False
        return {"CANCELLED"}


class DownloadFreeEnvironmentOperator(bpy.types.Operator):
    bl_idname = "gscatter.download_free_environment"
    bl_label = "Download Free Environment"
    bl_description = "Download free assets from Graswald"

    def execute(self, context):
        open_asset_browser(True)
        return {"FINISHED"}


classes = (
    ClosePopupOperator,
    DeleteScatterItemOperator,
    ToggleProxyOperator,
    ToggleVisibilityOperator,
    MoveScatterItemOperator,
    DuplicateScatterItemOperator,
    ScatterOperator,
    ScatterSelectedToActive,
    UpdateScatterSystemTreeOperator,
    AddNewSystemPresetOperator,
    RemovePresetOperator,
    ChangePresetOperator,
    MakeUniqueSystemOperator,
    SetSystemListOperator,
    CreateLinkedSystemOperator,
    DummyOperator,
    CreateEnvionmentFromTemplateOperator,
    BackOperator,
    DownloadFreeEnvironmentOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
