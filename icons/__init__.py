import glob
import os
from pathlib import Path

import bpy

from ..utils import startup
from ..utils.getters import get_preferences
from t3dn_bip import previews

previews.settings.WARNINGS = False

folder = Path(__file__).parent
collection: previews.ImagePreviewCollection = None
all_icons = {}


def load_icons_from_folder(folder_path: str):
    for i in glob.glob(folder_path + "/*.bip"):
        no_ext = os.path.splitext(i)[0]
        file_name = os.path.basename(no_ext)
        all_icons[file_name] = Path(i).as_posix()


def get(name: str) -> int:
    name = name.removesuffix(".bip") if name.endswith(".bip") else name
    if collection is None:
        return None
    icon = all_icons.get(name)
    if icon is None:
        icon = all_icons.get("not_selected")
    return collection.load_safe(icon, icon, "IMAGE").icon_id


def get_icon_path(name: str) -> int:
    name = name.removesuffix(".bip") if name.endswith(".bip") else name
    icon = all_icons.get(name)
    return icon


def get_all() -> list[str]:
    return all_icons.keys()


def is_custom(icon: str) -> bool:
    return icon.startswith("custom_")


def get_name_from_custom(icon: str) -> str:
    return icon.removeprefix("custom_").replace("_", " ").title()


def load_user_icons():
    prefs = get_preferences(bpy.context)
    store_path = Path(prefs.t3dn_library, "icons")
    if store_path.exists():
        load_icons_from_folder(store_path.as_posix())


def register():
    global collection
    global all_icons
    collection = previews.new(max_size=(32, 32), lazy_load=False)
    load_icons_from_folder(folder.as_posix())
    startup.add_callback(load_user_icons)


def unregister():
    previews.remove(collection)
    # bpy.utils.previews.remove(collection._collection)
