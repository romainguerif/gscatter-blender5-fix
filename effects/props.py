from typing import Iterator, Tuple, Union

import bpy

from ..utils.logger import debug

from .. import icons
from ..asset_manager.ops.popup import AssetBrowserPopup
from ..common.props import SceneProps, WindowManagerProps
from ..icon_viewer.ops import IconViewerPopup
from ..utils.getters import get_scene_props
from . import default
from .ops.effect_layers import (
    AddEffectInputToEffectPropertiesOperator,
    MakeUniqueEffectOperator,
    MoveEffectOperator,
    MuteEffectOperator,
    PaintWeightMapOperator,
    RenameEnvironmentPropertyOperator,
    SelectEffectOperator,
    SetEffectListOperator,
    ToggleLayerCollapseOperator,
)
from .store import effectstore
from .store.effect_item import Effect
from .store.utils import get_input_from_identifier


class VersionProps(bpy.types.PropertyGroup):
    major: bpy.props.IntProperty()
    minor: bpy.props.IntProperty()
    patch: bpy.props.IntProperty()

    original_version: bpy.props.IntVectorProperty()

    @property
    def original(self):
        return list(self.original_version)

    def set(self, version: Tuple[int, int, int]):
        self.major = version[0]
        self.minor = version[1]
        self.patch = version[2]
        self.original_version = version

    def __str__(self) -> str:
        return self.major + "." + self.minor + "." + self.patch

    def __iter__(self) -> Iterator[int]:
        return iter((self.major, self.minor, self.patch))

    def draw(self, layout: bpy.types.UILayout, context: bpy.types.Context, text=""):
        row = layout.row()
        row.prop(self, "major", text=text)
        row.prop(self, "minor", text="")
        row.prop(self, "patch", text="")


class EffectItemProps(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    effect_version: bpy.props.PointerProperty(type=VersionProps)
    author: bpy.props.StringProperty()

    @property
    def version(self):
        return list(self.effect_version)

    @version.setter
    def version(self, value):
        self.effect_version.set(value)


def update_effect_properties(wm_props, context):
    index = wm_props.effect_index
    try:
        effect_id = wm_props.effect_items[index].id
    except IndexError:
        return
    effect_version = wm_props.effect_items[index].version
    wm_props.effect_properties.set(
        effectstore.get_by_id_and_version(effect_id, effect_version)
    )


class BlendTypes(bpy.types.PropertyGroup):
    mix: bpy.props.BoolProperty(name="Mix", default=True)
    darken: bpy.props.BoolProperty(name="Darken", default=False)
    multiply: bpy.props.BoolProperty(name="Multiply", default=True)
    add: bpy.props.BoolProperty(name="Add", default=True)
    divide: bpy.props.BoolProperty(name="Divide", default=False)
    subtract: bpy.props.BoolProperty(name="Subtract", default=False)
    difference: bpy.props.BoolProperty(name="Difference", default=False)

    def get_enabled(self):
        items = []
        for blend_type in default.BLEND_TYPES:
            if getattr(self, blend_type.lower()):
                items.append(blend_type)
        return items

    def draw(self, layout: bpy.types.UILayout):
        box = layout.box()
        box.label(text="Blend Types")
        grid = box.grid_flow(align=True)
        for blend_type in default.BLEND_TYPES:
            grid.prop(self, blend_type.lower())

    def set(self, blend_types: list[str]):
        for blend_type in default.BLEND_TYPES:
            setattr(self, blend_type.lower(), False)

        for blend_type in blend_types:
            setattr(self, blend_type.lower(), True)


class EffectProps(bpy.types.PropertyGroup):
    effect_id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    author: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    icon: bpy.props.StringProperty()
    support_distribution: bpy.props.BoolProperty()
    support_scale: bpy.props.BoolProperty()
    support_rotation: bpy.props.BoolProperty()
    support_geometry: bpy.props.BoolProperty()
    blender_version: bpy.props.PointerProperty(type=VersionProps)
    effect_version: bpy.props.PointerProperty(type=VersionProps)
    blend_types: bpy.props.PointerProperty(type=BlendTypes, name="Blend Types")

    def _get_added_blend_types(self, context):
        self.blend_types: BlendTypes
        items = []
        for blend in self.blend_types.get_enabled():
            items.append((blend, blend.title(), ""))
        return items

    default_blend_type: bpy.props.EnumProperty(
        items=_get_added_blend_types, name="Default Blend Type"
    )
    subcategory: bpy.props.EnumProperty(
        items=[
            (subcategory, subcategory, f"The {subcategory} category")
            for subcategory in default.EFFECT_SUBCATEGORIES
        ],
    )

    @property
    def version(self):
        return list(self.effect_version)

    @property
    def blender_app_version(self):
        return list(self.blender_version)

    @property
    def categories(self):
        categories = []
        if self.support_distribution:
            categories.append("DISTRIBUTION")
        if self.support_scale:
            categories.append("SCALE")
        if self.support_rotation:
            categories.append("ROTATION")
        if self.support_geometry:
            categories.append("GEOMETRY")

        return categories

    def set(self, effect: Effect):
        self.effect_id = effect.id
        self.name = effect.name
        self.author = effect.author
        self.description = effect.description
        self.icon = effect.icon
        self.support_distribution = "DISTRIBUTION" in effect.categories
        self.support_scale = "SCALE" in effect.categories
        self.support_rotation = "ROTATION" in effect.categories
        self.support_geometry = "GEOMETRY" in effect.categories
        self.subcategory = effect.subcategory
        self.blender_version.set(effect.blender_version)
        self.effect_version.set(effect.effect_version)
        blend_types = getattr(effect, "blend_types", None)
        if blend_types:
            self.blend_types.set(blend_types)
        default_blend_type = getattr(effect, "default_blend_type", None)
        if default_blend_type:
            self.default_blend_type = default_blend_type

    def reset(self):
        self.effect_id = ""
        self.name = ""
        self.author = ""
        self.description = ""
        self.icon = "BLANK1"
        self.support_distribution = False
        self.support_scale = False
        self.support_rotation = False
        self.support_geometry = False
        self.subcategory = "Basic"
        self.blender_version.set(list(bpy.app.version))
        self.effect_version.set((1, 0, 0))

    def draw(self, layout: bpy.types.UILayout, context: bpy.types.Context):
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "name", text="Name")
        layout.prop(self, "author", text="Author")
        layout.prop(self, "description", text="Description")
        self.draw_icon(layout)

        layout.prop(self, "support_distribution", text="Distribution")
        layout.prop(self, "support_scale", text="Scale")
        layout.prop(self, "support_rotation", text="Rotation")
        layout.prop(self, "support_geometry", text="Geometry")

        layout.prop(self, "subcategory", text="Category")
        self.effect_version.draw(layout, context, "Effect Version")
        self.blender_version.draw(layout, context, "Blender Version")

        layout.prop(self, "default_blend_type")
        self.blend_types.draw(layout)

    def draw_icon(self, layout: bpy.types.UILayout):
        split = layout.row().split(factor=0.4)

        sub = split.row()
        sub.alignment = "RIGHT"
        sub.label(text="Icon")

        if icons.is_custom(self.icon):
            op = split.operator(
                IconViewerPopup.bl_idname,
                text=icons.get_name_from_custom(self.icon),
                icon_value=icons.get(self.icon),
            )
        else:
            icon = self.icon if self.icon else "NONE"
            op = split.operator(IconViewerPopup.bl_idname, text=icon, icon=icon)
        op.target = repr(self)

    def is_valid(self) -> bool:
        if self.name == "":
            return False
        if self.author == "":
            return False
        if self.description == "":
            return False
        if self.icon == "":
            return False
        if len(self.categories) == 0:
            return False
        return True


def on_update_blend_mode(self, context):
    if self.group_node:
        input = self.group_node.inputs.get(default.INPUT_BLEND_TYPE)
        if input:
            input.default_value = self.blend_type


def on_influence_update(self, context):
    if self.group_node:
        input = self.group_node.inputs.get(default.INPUT_INFLUENCE)
        if input:
            input.default_value = self.influence / 100


def on_invert_update(self, context):
    if self.group_node:
        input = self.group_node.inputs.get(default.INPUT_INVERT)
        if input:
            input.default_value = self.invert


class DropDownProps(bpy.types.PropertyGroup):
    def get_dropdown_items(self, context):
        items = []
        node: bpy.types.GeometryNode = self.node_group.nodes.get(self.name)
        if node:
            for output in node.outputs:
                if output.enabled and output.name not in [
                    "Main Geometry",
                    "Original Geometry",
                ]:
                    items.append((output.identifier, output.name, ""))
        return items

    def update_dropdown(self, context):
        connected_to_socket: bpy.types.NodeSocket = None
        node: bpy.types.GeometryNode = self.node_group.nodes.get(self.name)
        if node:
            for output in node.outputs:
                links: bpy.types.NodeLinks = output.links
                if links:
                    connected_to_socket = links[0].to_socket
                    self.node_group.links.remove(links[0])
                    break
            connect_from = None
            for output in node.outputs:
                if output.identifier == self.dropdown_items:
                    connect_from = output
            self.node_group.links.new(output=connect_from, input=connected_to_socket)

    name: bpy.props.StringProperty()
    node_group: bpy.props.PointerProperty(type=bpy.types.GeometryNodeTree)
    dropdown_items: bpy.props.EnumProperty(
        items=get_dropdown_items, update=update_dropdown
    )

    @property
    def label(self) -> str:
        node: bpy.types.GeometryNode = self.node_group.nodes.get(self.name)
        if node:
            return node.label if node.label else node.name
        else:
            return self.name

    @property
    def output_is_linked(self) -> bool:
        node: bpy.types.GeometryNode = self.node_group.nodes.get(self.name)
        for output in node.outputs:
            if output.identifier == self.dropdown_items:
                return not output.is_linked
        return False

    @property
    def linked_output(self) -> bpy.types.NodeSocket:
        node: bpy.types.GeometryNode = self.node_group.nodes.get(self.name)
        for output in node.outputs:
            if output.links:
                return output


class EffectLayerProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="ID", default="-1")
    effect_id: bpy.props.StringProperty(name="Effect ID", default="")  # ! Deppreciated
    effect_version: bpy.props.PointerProperty(
        name="Effect Version", type=VersionProps
    )  # ! Deppreciated
    icon: bpy.props.StringProperty(name="Icon")  # ! Deppreciated
    open: bpy.props.BoolProperty(default=True, name="Toggle Effect Layer Inputs")
    selected: bpy.props.BoolProperty(default=False)
    blend_types = ["ADD", "MULTIPLY", "MIX"]
    instance_id: bpy.props.StringProperty()

    def _on_influence_set(self, value):
        self["influence"] = value
        on_influence_update(self, bpy.context)

    def _influence_get(self):
        value = self.get("influence")
        if value is not None:
            return value
        return 100

    def _on_blend_type_set(self, value):
        self["blend_type"] = value
        on_update_blend_mode(self, bpy.context)

    def _blend_type_get(self):
        return self.get("blend_type")

    def _on_invert_set(self, value):
        self["invert"] = value
        on_invert_update(self, bpy.context)

    def _invert_get(self):
        value = self.get("invert")
        if value is not None:
            return value
        return 0

    def _get_blend_types(self, context):
        items = []
        for blend_type in self.blend_types:
            items.append((blend_type, blend_type.title(), ""))
        return items

    invert: bpy.props.BoolProperty(
        name="Invert",
        default=False,
        set=_on_invert_set,
        get=_invert_get,
    )
    blend_type: bpy.props.EnumProperty(
        name="Blend Type",
        items=_get_blend_types,
        set=_on_blend_type_set,
        get=_blend_type_get,
    )

    influence: bpy.props.IntProperty(
        name="Influence",
        default=100,
        min=0,
        max=100,
        soft_max=100,
        soft_min=0,
        subtype="PERCENTAGE",
        set=_on_influence_set,
        get=_influence_get,
    )

    dropdowns: bpy.props.CollectionProperty(type=DropDownProps)

    # * Please make sure to use below four methods instead of setting the properties in layer properties
    # * Effect id and Effect version should be stored in the effect node properties.
    def get_effect_id(self) -> str:
        effect_id = self.group_node.node_tree.gscatter.effect_id
        if not effect_id:
            return self.effect_id
        return effect_id

    def get_effect_version(self) -> list[int, int, int]:
        vers = self.group_node.node_tree.gscatter.version
        if not vers:
            return self.version
        return vers

    def set_effect_id(self, value):
        self.group_node.node_tree.gscatter.effect_id = value

    def set_effect_version(self, value):
        self.group_node.node_tree.gscatter.effect_version.set(value)

    # ! Deppreciated
    @property
    def version(self):
        """This property is deppreciated. Please use `get_effect_version()`"""
        return list(self.effect_version)

    # ! Deppreciated
    @version.setter
    def version(self, value):
        """This property is deppreciated. Please use `set_effect_version()`"""
        self.effect_version.set(value)

    @property
    def group_node(self) -> bpy.types.GeometryNodeGroup:
        node_tree: bpy.types.GeometryNodeTree = self.id_data
        return node_tree.nodes.get(self.name + "_group")

    @property
    def effect_node(self) -> bpy.types.GeometryNodeGroup:
        node_tree: bpy.types.GeometryNodeTree = self.id_data

        try:
            grp_input_node: bpy.types.GeometryNode = node_tree.nodes.get(
                self.name + "_group"
            ).node_tree.nodes["Group Input"]
            main_geo_link: bpy.types.NodeLink = grp_input_node.outputs[0].links
            if len(main_geo_link) > 0:
                effect_node = main_geo_link[0].to_node
                if effect_node and effect_node.name not in [
                    "visualizer" or "Group Output"
                ]:
                    effect_node_tree = getattr(effect_node, "node_tree", None)
                    if effect_node_tree is not None:
                        return effect_node
            return node_tree.nodes.get(self.name + "_group")
        except Exception:
            return node_tree.nodes.get(self.name + "_group")

    @property
    def mix_node(self) -> bpy.types.GeometryNode:
        mixer = self.effect_node.node_tree.nodes.get("mixer", None)
        if mixer is None:
            vis = self.group_node.node_tree.nodes.get("visualizer")
            if vis:
                mixer = vis.node_tree.nodes.get("mixer", None)
        return mixer

    def get_dropdown_node(self, node_tree, output_identifier):
        """
        Recursively gets all the nodes of type "GROUP" that are connected to the group output
        with the specified output_identifier.

        Args:
        - node_tree (bpy.types.GeometryNodeTree): the node tree to search in
        - output_identifier (str): the identifier of the group output to connect to

        Returns:
        - A node to display in UI
        """

        # First, find the group output node with the specified name.
        group_output = None
        for node in node_tree.nodes:
            if node.type == "GROUP_OUTPUT":
                group_output = node
                break

        if not group_output:
            # If no group output with the specified name is found, return an empty list.
            return []

        # Otherwise, recursively traverse the node tree starting from the group output.
        dropdown_node = None

        def traverse_node(node):
            nonlocal dropdown_node
            if node.gscatter.display_in_effect:
                dropdown_node = node
            else:
                for input in node.inputs:
                    for link in input.links:
                        if link.from_node:
                            traverse_node(link.from_node)

        traverse_input = None
        for input in group_output.inputs:
            if input.identifier == output_identifier:
                traverse_input = input
        if traverse_input:
            traverse_node_start = traverse_input.links[0].from_node
            traverse_node(traverse_node_start)

        return dropdown_node

    def draw_outputs_as_dropdown(
        self,
        context,
        scene_props,
        node: bpy.types.GeometryNode,
        layout: bpy.types.UILayout,
    ):
        dropdown: DropDownProps = self.dropdowns.get(node.name)
        if dropdown is None:
            return
        row = layout.row()
        row.alert = dropdown.output_is_linked
        row.prop(dropdown, "dropdown_items", text=dropdown.label)
        if node.type == "GROUP":
            node_tree: bpy.types.GeometryNodeTree = node.node_tree
            ui_node = self.get_dropdown_node(node_tree, dropdown.dropdown_items)
            if ui_node:
                if ui_node.type == "GROUP":
                    if ui_node.node_tree:
                        self.draw_node_group(
                            context, scene_props, ui_node.node_tree, layout
                        )
                self.draw_node(context, scene_props, ui_node, layout)

    def add_dropdown_items(self):
        if self.effect_node is None:
            return

        nodes = [
            node
            for node in self.effect_node.node_tree.nodes
            if isinstance(node, bpy.types.NodeInternal)
            and node.gscatter.display_in_effect
            and node.gscatter.display_output_as_dropdown
        ]
        if len(self.dropdowns) != len(nodes):
            debug("Clearing dropdowns")
            self.dropdowns.clear()
            for node in nodes:
                dropdown: DropDownProps = self.dropdowns.add()
                dropdown.name = node.name
                dropdown.node_group = self.effect_node.node_tree

                if dropdown.linked_output:
                    dropdown.dropdown_items = dropdown.linked_output.identifier

    def draw_inputs(
        self,
        context,
        scene_props,
        layout: bpy.types.UILayout,
        node: bpy.types.GeometryNode,
    ):
        for idx, input in enumerate(node.inputs):
            if input.name.endswith("Active Camera") and input.type == "OBJECT":
                continue
            if (
                not input.is_linked
                and hasattr(input, "default_value")
                and input.enabled
                and input.hide_value is False
            ):
                if input.type in ["IMAGE", "STRING"]:
                    split = layout.split(factor=0.38)
                    r = split.row()
                    r.alignment = "RIGHT"
                    r.label(text=input.name)
                    row = split.row()
                    row.use_property_split = False
                    row.alignment = "EXPAND"
                    if input.type == "STRING":
                        if input.name.endswith("Weight Map"):
                            r = row.row(align=True)
                            r.prop_search(
                                input,
                                "default_value",
                                scene_props.scatter_surface,
                                "vertex_groups",
                                text="",
                            )
                            painting = bpy.context.mode == "PAINT_WEIGHT"
                            op = r.operator(
                                PaintWeightMapOperator.bl_idname,
                                text="",
                                icon="BRUSH_DATA",
                                depress=painting,
                            )
                            op.effect_name = self.name
                            op.input_name = input.name
                        else:
                            row.prop(input, "default_value", text="")
                    else:
                        input.draw(context, row, self.effect_node, text="")
                    r = row.row()
                    r.enabled = False
                    r.scale_x = 0.8
                    r.label(text="", icon="BLANK1")
                elif input.type == "RGBA":
                    split = layout.split(factor=0.38)
                    r = split.row()
                    r.alignment = "RIGHT"
                    r.label(text=input.name)
                    row = split.row()
                    row.alignment = "EXPAND"
                    row.prop(input, "default_value", text="")

                elif input.type == "COLLECTION":
                    row = layout.row(align=True)
                    input.draw(context, row, self.effect_node, input.name)
                    op = row.operator(
                        AssetBrowserPopup.bl_idname,
                        text="",
                        icon="ASSET_MANAGER",
                    )
                    op.effect_name = self.name
                    op.input_name = input.name
                    op.use_mini_browser = True
                else:
                    # Draw Input
                    row = layout.row()
                    input.draw(context, row, self.effect_node, input.name)

                scene_props = get_scene_props(context)
                ss = scene_props.scatter_surface
                env_props = ss.gscatter.environment_props.props
                is_env_property = False
                for prop in env_props:
                    if (
                        prop.input == input.identifier
                        and prop.effect_instance_id == self.instance_id
                    ):
                        is_env_property = True

                if is_env_property:
                    re_op = row.operator(
                        RenameEnvironmentPropertyOperator.bl_idname,
                        text="",
                        icon="MODIFIER_ON",
                        emboss=False,
                        depress=True,
                    )
                    re_op.input = input.identifier
                    re_op.input_label = input.name
                else:
                    # Draw EnvrionmentProperty Operator
                    op = row.operator(
                        AddEffectInputToEffectPropertiesOperator.bl_idname,
                        text="",
                        icon="MODIFIER_OFF",
                        emboss=False,
                        depress=False,
                    )
                    op.effect_instance_id = self.instance_id
                    op.effect = self.group_node.node_tree.name
                    op.input = input.identifier
                    op.input_idx = idx
                    op.input_label = input.name

    def draw_node(
        self,
        context,
        scene_props,
        node: bpy.types.GeometryNode,
        layout: bpy.types.UILayout,
    ):
        if node.gscatter.display_output_as_dropdown:
            self.draw_outputs_as_dropdown(context, scene_props, node, layout)

        if node.gscatter.display_properties:
            if hasattr(node, "color_ramp") or node.type == "CURVE_FLOAT":
                node_box = layout.box()
                node.draw_buttons(context, node_box)
            else:
                layout.use_property_split = False
                node.draw_buttons(context, layout)

        if node.gscatter.display_inputs:
            self.draw_inputs(context, scene_props, layout, node)

    def draw_node_group(
        self,
        context,
        scene_props,
        node_group: bpy.types.GeometryNodeTree,
        layout: bpy.types.UILayout,
    ):
        nodes = [
            node
            for node in node_group.nodes
            if isinstance(node, bpy.types.NodeInternal)
            and node.gscatter.display_in_effect
        ]
        if len(nodes) > 0:
            nodes.sort(key=lambda node: node.gscatter.display_order)
            for node in nodes:
                self.draw_node(context, scene_props, node, layout)

        self.draw_inputs(context, scene_props, layout, self.effect_node)

    def draw(self, layout: bpy.types.UILayout, context: bpy.types.Context):
        # bpy.app.timers.register(self.add_dropdown_items, first_interval=0.1)
        self.add_dropdown_items()
        scene_props = get_scene_props(context)

        col = layout.column(align=True)
        box = col.box()
        box.scale_y = 1.3
        # Header
        row = box.row()
        row.separator(factor=0.05)
        sub = row.row(align=True)
        op = sub.operator(
            SelectEffectOperator.bl_idname,
            text="",
            icon_value=icons.get("selected.bip")
            if self.selected
            else icons.get("not_selected.bip"),
            emboss=False,
            depress=self.selected,
        )
        op.effect_name = self.name
        # op.category = self.category.category  # TODO
        # op.instance_id = self.instance_id

        # sub.prop(self, "open", text="", icon="DISCLOSURE_TRI_DOWN" if self.open else "DISCLOSURE_TRI_RIGHT", emboss=False,)
        op = sub.operator(
            ToggleLayerCollapseOperator.bl_idname,
            text="",
            emboss=False,
            icon="DISCLOSURE_TRI_DOWN" if self.open else "DISCLOSURE_TRI_RIGHT",
        )
        op.all = False
        op.all_except_current = False
        op.effect_name = self.name
        # op.category = self.category.category  # TODO

        if icons.is_custom(self.effect_node.node_tree.gscatter.icon):
            sub.label(icon_value=icons.get(self.effect_node.node_tree.gscatter.icon))
        else:
            sub.label(icon=self.effect_node.node_tree.gscatter.icon)
        sub.separator()
        sub_row = sub.row(align=True)
        sub_rr = sub_row.row(align=True)
        sub_rr.scale_x = 1.3
        op = sub_rr.operator_menu_enum(
            SetEffectListOperator.bl_idname, "type", text="", icon="NODETREE"
        )
        # op.category = self.category.category  # TODO
        op.node_name = self.group_node.name
        sub_row.prop(self.group_node.node_tree, "name", text="")
        sub_rr = sub_row.row(align=True)
        sub_rr.alignment = "LEFT"
        sub_rr.scale_x = 0.75
        if self.group_node.node_tree.users > 1:
            op = sub_rr.operator(
                MakeUniqueEffectOperator.bl_idname,
                text=str(self.group_node.node_tree.users),
            )
            # op.category = self.category.category  # TODO
            op.node_name = self.group_node.name
            op.effect_name = self.name

        sub = sub_row.row(align=True)
        sub.alignment = "RIGHT"
        op = sub.operator(MoveEffectOperator.bl_idname, text="", icon="TRIA_UP")
        op.up = True
        op.tooltip = "UP"
        op.effect_name = self.name
        # op.category = self.category.category # TODO
        op = sub.operator(MoveEffectOperator.bl_idname, text="", icon="TRIA_DOWN")
        op.up = False
        op.tooltip = "DOWN"
        op.effect_name = self.name
        # op.category = self.category.category  # TODO
        op = sub.operator(
            MuteEffectOperator.bl_idname,
            text="",
            icon="HIDE_ON" if self.group_node.mute else "HIDE_OFF",
            depress=self.group_node.mute,
        )
        op.node_name = self.group_node.name
        # op.category = self.category.category  # TODO
        # Body
        if self.open:
            box = col.box().row()
            box.label(icon="BLANK1")
            col = box.column()
            col.use_property_split = False
            col.use_property_decorate = True
            self.draw_node_group(context, scene_props, self.effect_node.node_tree, col)
            box.separator(factor=0.1)

            # Layout geometrynode modifier inputs on effect
            # if self.get_effect_id() == "system.instance_collection":
            #     c = self.group_node.inputs[1].default_value
            #     if c:
            #         for obj in c.all_objects:
            #             for mod in obj.modifiers:
            #                 if mod.type == 'NODES':
            #                     objbox = box.box()
            #                     objbox.label(text=obj.name)
            #                     for input in mod.node_group.inputs:
            #                         objbox.prop(mod, '["{}"]'.format(input.identifier), text=input.name)


class NodeTreeProps(bpy.types.PropertyGroup):
    # For top-level
    next_id: bpy.props.IntProperty(default=0)
    effects: bpy.props.CollectionProperty(type=EffectLayerProps)
    effect_category: bpy.props.StringProperty(default="NONE")

    effect_id: bpy.props.StringProperty()
    effect_version: bpy.props.PointerProperty(name="Effect Version", type=VersionProps)

    is_gscatter_effect: bpy.props.BoolProperty(default=False)
    effect_icon: bpy.props.StringProperty(default="BLANK1")

    @property
    def icon(self):
        if self.effect_icon == "BLANK1":
            effect = effectstore.get_by_id_and_version(self.effect_id, self.version)
            if effect is None:
                effect = effectstore.get_newest_by_id(self.effect_id)
            if effect is None:
                return "BLANK1"
            else:

                def set_icon():
                    if self.effect_icon == "BLANK1":
                        self.effect_icon = effect.icon
                        debug("Icon set")

                bpy.app.timers.register(set_icon, first_interval=0.1)
                return effect.icon
        else:
            return self.effect_icon

    @icon.setter
    def icon(self, value):
        self.effect_icon = value

    @property
    def category(self):
        return self.effect_category.split(",")

    @category.setter
    def category(self, value):
        self.effect_category = ",".join(value)

    @property
    def version(self):
        return list(self.effect_version)

    @version.setter
    def version(self, value):
        self.effect_version.set(value)

    def get_selected(self) -> Union[EffectLayerProps, None]:
        for effect in self.effects:
            effect: EffectLayerProps
            if effect.selected:
                return effect
        return None


class NodeInternalProps(bpy.types.PropertyGroup):
    display_in_effect: bpy.props.BoolProperty(default=False)
    display_order: bpy.props.IntProperty(default=0)
    display_output_as_dropdown: bpy.props.BoolProperty(default=False)
    display_properties: bpy.props.BoolProperty(default=True)
    display_inputs: bpy.props.BoolProperty(default=False)


def update_effect_type_toggle(self, context):
    context.window_manager.gscatter.effect_index = -1
    context.window_manager.gscatter.effect_properties.reset()


class EffectManagerProps(bpy.types.PropertyGroup):
    effect_type_toggle: bpy.props.EnumProperty(
        name="Effect Type",
        items=[
            ("INTERNAL", "Internal", "Show internal Effects", "", 0),
            ("SYSTEM", "System", "Show System Effects", "", 1),
            ("USER", "User", "Show User Effects", "", 2),
        ],
        default="USER",
        update=update_effect_type_toggle,
    )


class GscatterCollectionProp(bpy.types.PropertyGroup):
    is_gscatter_asset: bpy.props.BoolProperty(default=False)
    asset_id: bpy.props.StringProperty()


classes = (
    VersionProps,
    DropDownProps,
    EffectLayerProps,
    BlendTypes,
    EffectProps,
    NodeTreeProps,
    EffectItemProps,
    NodeInternalProps,
    EffectManagerProps,
    GscatterCollectionProp,
)


def update_visualization_resolution(self, context):
    get_scene_props(bpy.context)
    ss = bpy.data.objects.get("gscatter_viz_obj")
    if ss:
        mod = ss.modifiers.get("gscater_viz_modifier")
        if mod:
            viz_tree = mod.node_group

            if viz_tree:
                subdivide_node = viz_tree.nodes.get("subdivide_mesh")

                if subdivide_node:
                    level = get_input_from_identifier(subdivide_node.inputs, "Level")
                    level.default_value = self.visualization_resolution - 1


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    WindowManagerProps.effect_items = bpy.props.CollectionProperty(type=EffectItemProps)
    WindowManagerProps.effect_index = bpy.props.IntProperty(
        update=update_effect_properties
    )
    WindowManagerProps.effect_properties = bpy.props.PointerProperty(type=EffectProps)
    SceneProps.active_category = bpy.props.EnumProperty(
        items=[
            ("DISTRIBUTION", "Distribution", "", 1),
            ("SCALE", "Scale", "", 2),
            ("ROTATION", "Rotation", "", 3),
            ("GEOMETRY", "Geometry", "", 4),
        ]
    )
    WindowManagerProps.effect_manager_props = bpy.props.PointerProperty(
        type=EffectManagerProps
    )
    WindowManagerProps.show_environment_presets_list = bpy.props.BoolProperty(
        default=False
    )
    WindowManagerProps.show_camera_culling_exluce_list = bpy.props.BoolProperty(
        default=False
    )
    SceneProps.visualizing = bpy.props.BoolProperty(default=False)
    WindowManagerProps.show_visualizer = bpy.props.BoolProperty(default=False)
    WindowManagerProps.can_be_visualized = bpy.props.BoolProperty(default=True)
    SceneProps.visualize_mode = bpy.props.EnumProperty(
        items=[
            ("OFF", "Off", "Visualize mode off", "", 0),
            ("ALL", "All Effects", "Visualize all effects", "", 1),
            ("SELECTED", "Selected", "Visualize selected effect", "", 2),
        ],
    )

    bpy.types.NodeTree.gscatter = bpy.props.PointerProperty(type=NodeTreeProps)
    bpy.types.NodeInternal.gscatter = bpy.props.PointerProperty(type=NodeInternalProps)
    bpy.types.Collection.gscatter = bpy.props.PointerProperty(
        type=GscatterCollectionProp
    )
    SceneProps.visualization_resolution = bpy.props.IntProperty(
        name="Visualizer Mesh Resolution",
        description="Non-descructively increase the mesh density\nfor a more detailed view",
        default=1,
        min=1,
        soft_min=1,
        max=7,
        soft_max=7,
        update=update_visualization_resolution,
    )


def unregister():
    del bpy.types.NodeInternal.gscatter
    del (
        bpy.types.NodeTree.gscatter
    )  # Not using GeometryNodeTree, because it errors on unregister.

    del SceneProps.active_category
    del WindowManagerProps.effect_properties
    del WindowManagerProps.effect_index
    del WindowManagerProps.effect_items
    del WindowManagerProps.effect_manager_props
    del WindowManagerProps.show_environment_presets_list
    del WindowManagerProps.show_camera_culling_exluce_list
    del SceneProps.visualizing
    del WindowManagerProps.show_visualizer
    del WindowManagerProps.can_be_visualized
    del SceneProps.visualize_mode
    del bpy.types.Collection.gscatter
    del SceneProps.visualization_resolution

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
