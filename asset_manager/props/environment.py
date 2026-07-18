import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    StringProperty,
    PointerProperty,
)
from bpy.types import UILayout
from .previews import PreviewsWidget
from .base import BaseWidget
from .. import previews
from ..ops.popup import ReadDescriptionPopup, OpenPreviewPopup
from ..ops.misc import SelectItemOperator, DummyOperator
from ...utils import wrap_text
from ...scatter.utils import draw_terrain_selector
from ...utils.getters import get_wm_props

environment_datas = {}


class EnvironmentPropItem(BaseWidget):
    effect_instance_id: StringProperty()
    input: StringProperty()
    input_idx: IntProperty()
    order_idx: IntProperty()
    input_type: StringProperty()
    input_label: StringProperty()

    collection: PointerProperty(name="Collection", type=bpy.types.Collection)
    object: PointerProperty(name="Object", type=bpy.types.Object)

    def draw(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        if self.input_type == "COLLECTION":
            layout.prop_search(
                self, "collection", bpy.data, "collections", text=self.input_label
            )
        elif self.input_type == "OBJECT":
            layout.prop_search(
                self, "object", context.view_layer, "objects", text=self.input_label
            )

    def get_prop_value(self):
        if self.input_type == "COLLECTION":
            return self.collection
        elif self.input_type == "OBJECT":
            return self.object


class EnvironmentWidget(BaseWidget):
    name: StringProperty(name="Name")
    asset_id: StringProperty(name="Asset Id")
    description: StringProperty(name="Description")
    tags: CollectionProperty(name="Tags", type=BaseWidget)
    author: StringProperty(name="Author")
    previews: PointerProperty(name="Previews", type=PreviewsWidget)
    select: BoolProperty(name="Select", default=False)
    blends: CollectionProperty(name="Blends", type=BaseWidget)
    use_default_terrain: BoolProperty(name="Use Environment Terrain", default=True)
    use_terrain_material: BoolProperty(name="Use Terrain Material", default=True)
    use_custom_assets: BoolProperty(default=False)
    show_gscatter_assets: BoolProperty(default=False)
    environment_props: CollectionProperty(type=EnvironmentPropItem)

    def get_prop(self, instance_id, input_idx):
        for prop in self.environment_props:
            if prop.effect_instance_id == instance_id and input_idx == prop.input_idx:
                return prop

    @property
    def environment_dict(self):
        return environment_datas[self.asset_id]

    @property
    def systems(self):
        return environment_datas[self.asset_id]["gscatter_systems"]

    @property
    def gscatter_assets(self):
        return environment_datas[self.asset_id]["gscatter_assets"]

    def load(self, data: dict):
        self.name = data.get("name", "")
        self.asset_id = data.get("asset_id", "")
        self.description = data.get("description", "")
        self.author = data.get("author", {})
        self.previews.load(data.get("previews", {}))
        environment_datas[self.asset_id] = data

        self.blends.clear()
        for path in data.get("blends", []):
            blend = self.blends.add()
            blend.name = path

        self.environment_props.clear()
        for prop in data.get("environment_props", []):
            env_prop: EnvironmentPropItem = self.environment_props.add()
            env_prop.effect_instance_id = prop["effect_instance_id"]
            env_prop.input = prop["input"]
            env_prop.input_idx = prop["input_idx"]
            env_prop.input_label = prop["label"]
            env_prop.input_type = prop["input_type"]
            env_prop.order_idx = prop["order_idx"]

        # self.tags.clear()
        # for name in data.get('tags', []):
        #     tag = self.tags.add()
        #     tag.name = name

    def draw_gallery(self, layout: UILayout):
        box = layout.box()
        self.previews.draw_gallery(box)
        row = layout.row(align=True)
        row.scale_y = 1.6
        op = row.operator(
            SelectItemOperator.bl_idname, text=self.name, depress=self.select
        )
        op.target, op.deselect = repr(self), False

    def draw_template(self, layout: UILayout, width=200):
        row = layout.row()
        sub_row = row.row()
        sub_row.alignment = "LEFT"
        sub_row.label(text=self.name)
        sub_row = row.row()
        sub_row.enabled = False
        sub_row.alignment = "RIGHT"
        sub_row.label(text=self.author)

    def draw_environment_setup(self, layout):
        col = layout.box().column()
        row = col.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "use_custom_assets", text="Override assets")

        if self.use_custom_assets:
            col = col.column()
            col.enabled = self.use_custom_assets
            col.use_property_split = True
            for prop in self.environment_props:
                prop: EnvironmentPropItem
                prop.draw(bpy.context, col)

    def draw_details(self, layout: UILayout):
        wm_props = get_wm_props(bpy.context)
        starter_props = wm_props.scatter_starter

        main_col = layout.column(align=True)

        box = main_col.box()
        self.previews.draw_details(box)
        detail_path = self.previews.details[0].name
        preview = previews.get(detail_path)
        preview.icon_size = [1500, 1500]
        icon_id = preview.icon_id

        row = main_col.box().row()
        row.box().operator(
            DummyOperator.bl_idname, text=self.name, emboss=False, depress=True
        )

        box = main_col.box()
        text_col = box.column(align=True)
        text_col.scale_y = 0.8
        op = row.operator(OpenPreviewPopup.bl_idname, text="", icon="SEQ_PREVIEW")
        op.icon_id = repr(icon_id)

        text_lines = wrap_text(
            self.description, max(min(bpy.context.region.width * 1.5, 700), 400)
        )
        for id, text in enumerate(text_lines):
            if id < 2 and id < len(text_lines) - 2:
                text_col.label(text=text)
                # text_col.prop_with_popover(self, "description", text="Read more...")
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

        row = box.row()
        row.alignment = "RIGHT"
        row.label(text=f"by {self.author}")

        self.draw_environment_setup(layout)

        parent = self.parent
        assets = []
        for asset in self.gscatter_assets:
            the_asset = [
                product for product in parent.products if product.asset_id == asset
            ]
            if the_asset:
                assets.append((True, the_asset[0]))
            else:
                assets.append((False, asset))

        main_col.separator()
        draw_terrain_selector(main_col, starter_props)


classes = (
    EnvironmentPropItem,
    EnvironmentWidget,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
