import bpy

from t3dn_bip import previews

previews.settings.WARNINGS = False
collection = None


def get(path: str) -> bpy.types.ImagePreview:
    return collection.load_safe(path, path, "IMAGE")


def register():
    global collection
    collection = previews.new(max_size=(1024, 1024))


def unregister():
    # bpy.utils.previews.remove(collection._collection)
    previews.remove(collection)
