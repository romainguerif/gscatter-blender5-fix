import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup
from ..common.props import SceneProps, ObjectProps
import bpy.utils.previews


class EnvironmentCreatorProps(PropertyGroup):
    def update_preview(self, context):
        if self.preview.startswith("//"):
            self.preview = bpy.path.abspath(self.preview)

    def update_name(self, context):
        if self.name.startswith(" ") or self.name.endswith(" "):
            self.name = self.name.strip()

    name: StringProperty(name="Name", default="New Environment", update=update_name)
    description: StringProperty(name="Description")
    author: StringProperty(name="Author")
    preview: StringProperty(
        name="Preview",
        description="Preview image of the Environment",
        # subtype="FILE_PATH",
        update=update_preview,
    )
    terrain_material: PointerProperty(name="Terrain Material", type=bpy.types.Material)
    show_systems: BoolProperty(default=False, name="Show System List")


class EnvironmentPropItem(PropertyGroup):
    label: StringProperty(name="Label")
    type: EnumProperty(
        name="Property Type",
        items=[
            ("POINTER", "Pointer", "Pointer property to effect inputs"),
            ("INT", "Integer", "Integer Property"),
        ],
    )
    effect_instance_id: StringProperty(name="Instance ID")
    input: StringProperty(name="Input")
    input_idx: IntProperty(name="Input Index")
    order_idx: IntProperty()


class ObjectEnvironmentProps(PropertyGroup):
    props: CollectionProperty(name="Environment Properties", type=EnvironmentPropItem)
    editing: BoolProperty(
        name="Toggle editing of Environment Properties.", default=False
    )


classes = (EnvironmentCreatorProps, EnvironmentPropItem, ObjectEnvironmentProps)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    SceneProps.environment_creator = PointerProperty(type=EnvironmentCreatorProps)
    ObjectProps.environment_props = PointerProperty(type=ObjectEnvironmentProps)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del SceneProps.environment_creator
    del ObjectProps.environment_props
