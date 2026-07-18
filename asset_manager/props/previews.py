import bpy
from bpy.props import CollectionProperty, IntProperty, StringProperty
from bpy.types import UILayout

from .. import previews, utils
from .base import BaseWidget


class PreviewsWidget(BaseWidget):
    gallery: StringProperty(name="Gallery")
    details: CollectionProperty(name="Details", type=BaseWidget)
    index: IntProperty(name="Index", default=0)

    def load(self, data: dict):
        self.gallery = data.get("gallery", "")

        self.details.clear()
        for path in data.get("details", []):
            detail = self.details.add()
            detail.name = path

    def draw_gallery(self, layout: UILayout):
        icon_id = previews.get(self.gallery).icon_id
        layout.template_icon(icon_id, scale=utils.icon_scale_from_res(173))

    def draw_details(self, layout: UILayout):
        detail_path = self.details[self.index].name
        icon_id = previews.get(detail_path).icon_id
        layout.template_icon(icon_id, scale=utils.icon_scale_from_res(300))

    @staticmethod
    def draw_blank(layout: UILayout):
        layout.template_icon(0, scale=utils.icon_scale_from_res(173))

    def get_gallery_preview(self):
        icon_id = previews.get(self.gallery).icon_id
        return icon_id


classes = (PreviewsWidget,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
