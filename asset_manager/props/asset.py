import bpy
from bpy.props import BoolProperty, CollectionProperty, StringProperty, PointerProperty
from bpy.types import UILayout

from ...common.ops import OpenUrlOperator
from ...utils import wrap_text
from ..ops.misc import (
    DummyOperator,
    ScrollDetailsOperator,
    SelectItemOperator,
    UseItemOperator,
)
from ..ops.popup import OpenPreviewPopup, ReadDescriptionPopup
from .asset_configurator import AssetConfiguratorWidget
from .author import AuthorWidget
from .base import BaseWidget
from .previews import PreviewsWidget
from .. import previews


class AssetWidget(BaseWidget):
    name: StringProperty(name="Name")
    variant: StringProperty(name="Variant")
    asset_id: StringProperty(name="Asset Id")
    description: StringProperty(name="Description")
    tags: CollectionProperty(name="Tags", type=BaseWidget)
    url: StringProperty(name="URL")
    author: PointerProperty(name="Author", type=AuthorWidget)
    previews: PointerProperty(name="Previews", type=PreviewsWidget)
    blends: CollectionProperty(name="Blends", type=BaseWidget)
    configurator: PointerProperty(name="Configurator", type=AssetConfiguratorWidget)
    select: BoolProperty(name="Select", default=False)
    asset_browser_select: BoolProperty(name="Select", default=True)
    product_name: StringProperty(name="Product Name")

    def load(self, data: dict):
        self.name = data.get("name", "")
        self.product_name = data.get("product_name", "")
        self.asset_id = data.get("asset_id", "")
        self.description = data.get("description", "")
        self.url = data.get("url", "")
        self.author.load(data.get("author", {}))
        self.previews.load(data.get("previews", {}))
        self.configurator.load(data.get("configurator", {}))

        self.tags.clear()
        for name in data.get("tags", []):
            tag = self.tags.add()
            tag.name = name

        self.blends.clear()
        for path in data.get("blends", []):
            blend = self.blends.add()
            blend.name = path

    def draw_selector(self, layout: UILayout):
        row = layout.row()
        row.prop(self, "asset_browser_select", text=self.name)
        op = row.operator(
            OpenUrlOperator.bl_idname, text="", icon="QUESTION", emboss=False
        )
        OpenUrlOperator.configure(op, self.url, "openAssetInfoPage", "Asset", self.name)

    def draw_gallery(self, layout: UILayout):
        box = layout.box()
        self.previews.draw_gallery(box)
        row = layout.row(align=True)
        row.scale_y = 1.6
        op = row.operator(
            SelectItemOperator.bl_idname, text=self.name, depress=self.select
        )
        op.target, op.deselect = repr(self), False

    def draw_details(self, layout: UILayout):
        main_col = layout.column(align=True)
        box = main_col.box()
        self.previews.draw_details(box)
        detail_path = self.previews.details[0].name
        preview = previews.get(detail_path)
        preview.icon_size = [1500, 1500]
        icon_id = preview.icon_id

        row = main_col.box().row()
        op = row.operator(
            ScrollDetailsOperator.bl_idname, text="", icon="TRIA_LEFT", emboss=False
        )
        op.previews = repr(self.previews)
        op.direction = -1
        row.operator(
            DummyOperator.bl_idname, text=self.name, emboss=False, depress=True
        )

        op = row.operator(OpenPreviewPopup.bl_idname, text="", icon="SEQ_PREVIEW")
        op.icon_id = repr(icon_id)

        op = row.operator(
            ScrollDetailsOperator.bl_idname, text="", icon="TRIA_RIGHT", emboss=False
        )
        op.previews = repr(self.previews)
        op.direction = 1

        if self.description:
            box = main_col.box()
            text_col = box.column(align=True)
            text_col.scale_y = 0.8
            text_lines = wrap_text(self.description, bpy.context.region.width)
            for id, text in enumerate(text_lines):
                if id < 2 and id < len(text_lines) - 2:
                    text_col.label(text=text)
                else:
                    text_col.label(text=f"{text}...")
                    text_col.separator()
                    row = text_col.row()
                    row.alignment = "LEFT"
                    op = row.operator(
                        ReadDescriptionPopup.bl_idname,
                        text="...read all.",
                        emboss=True,
                        depress=False,
                    )
                    op.name = self.name
                    op.description = self.description
                    break

        box = main_col.box()
        row = box.row()
        self.draw_more_info(row)
        self.author.draw(row)

    def draw_more_info(self, layout: UILayout):
        if not self.url:
            return

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.scale_x = 0.8

        op = row.operator(OpenUrlOperator.bl_idname, text="More Info", emboss=False)
        OpenUrlOperator.configure(op, self.url, "openAssetInfoPage", "Asset", self.name)

        op = row.operator(
            OpenUrlOperator.bl_idname, text="", icon="RIGHTARROW", emboss=False
        )
        OpenUrlOperator.configure(op, self.url, "openAssetInfoPage", "Asset", self.name)

    def draw_list_item(self, layout: UILayout):
        row = layout.row()
        row.label(text=self.name)

        row = row.row()
        row.alignment = "RIGHT"
        op = row.operator(SelectItemOperator.bl_idname, text="", icon="X", emboss=False)
        op.target = repr(self)
        op.deselect = True

    def draw_item(self, layout: UILayout, effect_name: str, input_name: str):
        row = layout.row(align=True)
        row.scale_y = 1.6
        op = row.operator(UseItemOperator.bl_idname, text=self.name)
        op.target = repr(self)
        op.effect_name = effect_name
        op.input_name = input_name

        box = layout.box()
        self.previews.draw_gallery(box)

    @staticmethod
    def draw_blank(layout: UILayout):
        box = layout.column()
        PreviewsWidget.draw_blank(box)

        row = layout.row(align=True)
        row.enabled = False
        row.scale_y = 1.6
        row.operator(DummyOperator.bl_idname, text=" ", emboss=False, depress=False)


classes = (AssetWidget,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
