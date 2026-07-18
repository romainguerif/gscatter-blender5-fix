from ..utils.logger import debug
from ..common.props import WindowManagerProps
from bpy.types import PropertyGroup, Object
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.utils import register_class, unregister_class
import bpy
from bpy.app.handlers import persistent


class ScatterStarterProps(PropertyGroup):
    terrain_type: EnumProperty(
        name="Terrain type",
        items=[
            ("DEFAULT", "Default", "Use Environment's default terrain"),
            ("CUSTOM", "Custom", "Use custom terrain"),
            ("NEW", "New Terrain", "Create a new terrain from terrain templates"),
        ],
    )
    terrain_scale: IntProperty(name="Terrain Scale", default=1)
    custom_terrain: PointerProperty(name="Terrain", type=Object)
    use_environment_template: BoolProperty(default=False)
    use_terrain_material: BoolProperty(default=True)


# Custom property class to hold data entries
class DataEntry(PropertyGroup):
    name: StringProperty()
    index = IntProperty(name="Index", default=0)


@persistent
def init_first_entry(self=None, context=None):
    debug("Creating first entry")
    if len(bpy.context.window_manager.gscatter.empty_list) < 1:
        entry = bpy.context.window_manager.gscatter.empty_list.add()
        entry.name = "An Empty List Item"
        entry.index = -1


classes = (ScatterStarterProps, DataEntry)


def register():
    for cls in classes:
        register_class(cls)

    WindowManagerProps.scatter_starter = PointerProperty(type=ScatterStarterProps)
    WindowManagerProps.empty_list = CollectionProperty(type=DataEntry)
    WindowManagerProps.empty_index = IntProperty(default=-1)
    bpy.app.handlers.load_post.append(init_first_entry)


def unregister():
    for cls in classes:
        unregister_class(cls)

    del WindowManagerProps.scatter_starter
    del WindowManagerProps.empty_list
    del WindowManagerProps.empty_index
    bpy.app.handlers.load_post.remove(init_first_entry)
