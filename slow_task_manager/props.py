from bpy.types import PropertyGroup
import bpy
from bpy.props import CollectionProperty, IntProperty, StringProperty, PointerProperty
from ..common.props import WindowManagerProps


class TaskItem(PropertyGroup):
    name: StringProperty()
    progress: IntProperty(min=0, max=100, subtype="PERCENTAGE")
    progress_text: StringProperty()


class SlowTaskProps(PropertyGroup):
    tasks: CollectionProperty(type=TaskItem)


classes = (TaskItem, SlowTaskProps)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    WindowManagerProps.slow_task = PointerProperty(type=SlowTaskProps)


def unregister():
    del WindowManagerProps.slow_task

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
