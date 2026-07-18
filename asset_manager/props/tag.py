import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import UILayout

from ..ops.misc import SelectItemOperator
from .base import BaseWidget


class TagWidget(BaseWidget):
    name: StringProperty(name="Name")
    select: BoolProperty(name="Select")

    def draw(self, layout: UILayout):
        op = layout.operator(
            SelectItemOperator.bl_idname, text=self.name, depress=self.select
        )
        op.target = repr(self)
        op.deselect = False


classes = (TagWidget,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
