from .base import BaseWidget
from bpy.types import UILayout
from .previews import PreviewsWidget
from bpy.props import BoolProperty, CollectionProperty, StringProperty, PointerProperty
from .asset import AssetWidget
from .author import AuthorWidget
import bpy
from ...utils import wrap_text


class ProductWidget(BaseWidget):
    id: StringProperty()
    previews: PointerProperty(name="Previews", type=PreviewsWidget)
    assets: CollectionProperty(name="Assets", type=AssetWidget)
    description: StringProperty(name="Description")
    authors: CollectionProperty(name="Author", type=AuthorWidget)
    ecosystem: StringProperty(name="Ecosystem")
    expanded: BoolProperty(default=True)

    def load(self, data: dict):
        self.id = data["product_id"]
        self.name = data["name"]
        self.description = data["description"]
        self.ecosystem = data["ecosystem"]

        self.previews.load(data.get("previews", {}))

        for author in data["authors"].values():
            new_author = self.authors.add()
            new_author.load(author)

        for asset in data["assets"]:
            new_asset = self.assets.add()
            new_asset.load(asset)

    def draw(self, layout: UILayout):
        col = layout.column(align=True)
        self.previews.draw_details(col.box())
        col.box().operator("gscatter.dummy", text=self.name, emboss=False, depress=True)

        box = col.box()
        text_col = box.column(align=True)
        text_col.scale_y = 0.8
        width = bpy.context.region.width
        for text in wrap_text(self.description, width):
            text_col.label(text=text)
        col = box.column(align=True)
        # col.label(text=f"Ecosystem: {self.ecosystem}")
        row = col.row()
        for author in self.authors:
            author.draw(row)

        col = layout.column(align=True)
        col.box().label(text="Select variant for scattering")

        box = col.box()

        for asset in self.assets:
            asset.draw_selector(box)


classes = (ProductWidget,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
