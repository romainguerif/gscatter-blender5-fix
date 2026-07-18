import bpy
from bpy.props import CollectionProperty, StringProperty

from .base import BaseWidget


class AssetAttributeWidget(BaseWidget):
    name: StringProperty(name="Name")
    value: StringProperty(name="Value")

    def load(self, data: dict):
        self.name = data.get("name", "")
        self.value = data.get("value", "")


class AssetPropertyWidget(BaseWidget):
    name: StringProperty(name="Name")
    items: CollectionProperty(name="Items", type=BaseWidget)

    @property
    def value(self) -> str:
        configurator = self.parent
        asset = configurator.parent
        library = asset.parent

        if configurator.name in library.configurators:
            configurator = library.configurators[configurator.name]
        else:
            configurator = library.configurators["standard"]

        return configurator.properties[self.name].value

    def load(self, data: dict):
        self.name = data.get("name", "")

        self.items.clear()
        for name in data.get("items", []):
            item = self.items.add()
            item.name = name


class AssetConfiguratorWidget(BaseWidget):
    name: StringProperty(name="Name")
    attributes: CollectionProperty(name="Attributes", type=AssetAttributeWidget)
    properties: CollectionProperty(name="Properties", type=AssetPropertyWidget)

    def load(self, data: dict):
        self.name = data.get("name", "")

        self.attributes.clear()
        for name, value in data.get("attributes", {}).items():
            attr = self.attributes.add()
            attr.load({"name": name, "value": value})

        self.properties.clear()
        for name, items in data.get("properties", {}).items():
            prop = self.properties.add()
            prop.load({"name": name, "items": items})


classes = (
    AssetAttributeWidget,
    AssetPropertyWidget,
    AssetConfiguratorWidget,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
