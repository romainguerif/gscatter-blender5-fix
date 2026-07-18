import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, StringProperty
from bpy.types import Context, UILayout

from .base import BaseWidget


class LibraryPropertyWidget(BaseWidget):
    name: StringProperty(name="Name")
    available_items: CollectionProperty(name="Available Items", type=BaseWidget)
    selectable_items: CollectionProperty(name="Selectable Items", type=BaseWidget)
    default_items: CollectionProperty(name="Default Items", type=BaseWidget)

    def enum_items(self, context: Context) -> list:
        items = self.selectable_items.keys()
        return [(name, name, "") for name in items]

    def update_value(self, context: Context):
        self.value_backup = self.value

    value: EnumProperty(name="Value", items=enum_items, update=update_value)
    value_backup: StringProperty(name="Value Backup")
    valid: BoolProperty(name="Valid")

    def refresh_items(self):
        configurator = self.parent
        library = configurator.parent
        assets = library.selected_assets()
        matching_items = set(self.available_items.keys())

        for asset in assets:
            if asset.configurator.name == configurator.name:
                properties = asset.configurator.properties

                if self.name in properties:
                    items = set(properties[self.name].items.keys())
                    matching_items.intersection_update(items)
                else:
                    matching_items.clear()

                if not matching_items:
                    break

        # If it's a single asset, properties are optional.
        if len(assets) == 1:
            self.valid = True
        else:
            self.valid = bool(matching_items)

        self.selectable_items.clear()
        for name in self.available_items.keys():
            if name in matching_items:
                item = self.selectable_items.add()
                item.name = name

    def refresh_value(self):
        items = [self.value_backup] + self.default_items.keys()

        for name in items:
            if name in self.selectable_items:
                self.value = name
                break

    def load(self, data: dict):
        self.name = data.get("name", "")

        self.available_items.clear()
        for name in data.get("items", []):
            item = self.available_items.add()
            item.name = name

        self.selectable_items.clear()
        for name in data.get("items", []):
            item = self.selectable_items.add()
            item.name = name

        self.default_items.clear()
        for name in data.get("defaults", []):
            item = self.default_items.add()
            item.name = name

        self.refresh_value()

    def draw(self, layout: UILayout):
        split = layout.split(factor=0.4, align=True)

        left = split.row(align=True)
        right = split.row(align=True)

        left.alignment = "RIGHT"
        left.label(text=self.name)

        if self.selectable_items:
            right.prop(self, "value", text="")
        elif self.valid:
            right.label(text="No Options")
        else:
            right.alert = True
            right.label(text="No Valid Options")


class LibraryConfiguratorWidget(BaseWidget):
    name: StringProperty(name="Name")
    properties: CollectionProperty(name="Properties", type=LibraryPropertyWidget)

    def refresh_properties(self):
        for prop in self.properties:
            prop.refresh_items()
            prop.refresh_value()

    def check_properties(self) -> bool:
        return not self.properties or all(prop.valid for prop in self.properties)

    def load(self, data: dict):
        self.name = data.get("name", "")

        self.properties.clear()
        for name, prop_data in data.get("properties", {}).items():
            prop = self.properties.add()
            prop.load(
                {
                    "name": name,
                    "items": prop_data.get("items", []),
                    "defaults": prop_data.get("defaults", []),
                }
            )

    def draw_properties(self, layout: UILayout):
        box = layout.box()

        if any(prop.selectable_items for prop in self.properties):
            col = box.column(align=True)
            col.scale_x, col.scale_y = 1.4, 1.4

            for prop in self.properties:
                prop.draw(col)

        else:
            split = box.split(factor=0.4, align=True)

            _ = split.row(align=True)
            right = split.row(align=True)

            right.enabled = False
            right.label(text="No Properties")
        return box


classes = (
    LibraryPropertyWidget,
    LibraryConfiguratorWidget,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
