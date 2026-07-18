import bpy
from bpy.props import StringProperty
from bpy.types import PropertyGroup, bpy_prop_collection


class BaseWidget(PropertyGroup):
    """The base class for all widgets."""

    name: StringProperty(name="Name")

    @property
    def parent(self) -> "BaseWidget":
        """The property group this widget is in."""
        return eval(repr(self).rpartition(".")[0])

    @property
    def parent_collection(self) -> "bpy_prop_collection":
        """The collection this widget is in."""
        return eval(repr(self).rpartition("[")[0])


classes = (BaseWidget,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
