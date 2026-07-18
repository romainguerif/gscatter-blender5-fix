import bpy
from bpy.props import StringProperty
from bpy.types import UILayout

from ...common.ops import OpenUrlOperator
from .. import previews
from .base import BaseWidget


class AuthorWidget(BaseWidget):
    name: StringProperty(name="Name")
    icon: StringProperty(name="Icon")
    url: StringProperty(name="URL")

    def load(self, data: dict):
        self.name = data.get("name", "")
        self.icon = data.get("icon", "")
        self.url = data.get("url", "")

    def draw(self, layout: UILayout):
        row = layout.row()
        row.alignment = "RIGHT"

        preview = previews.get(self.icon)
        # preview.icon_size = preview.image_size
        # preview.icon_pixels = preview.image_pixels

        op = row.operator(
            OpenUrlOperator.bl_idname,
            text=self.name,
            icon_value=preview.icon_id,
            emboss=False,
        )
        OpenUrlOperator.configure(
            op, self.url, "openAuthorInfoPage", "Author", self.name
        )


classes = (AuthorWidget,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
