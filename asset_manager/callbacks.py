import bpy
from bpy.app.handlers import persistent

from ..utils.logger import debug
from ..utils.startup import add_callback
from ..utils.getters import get_preferences
from bpy.types import UserAssetLibrary
from . import default
from .asset_browser import refresh_library
from ..utils.getters import get_asset_browser_dir, get_user_library
from .utils import load_library


def create_gscatter_asset_browser_entry():
    context = bpy.context
    library = get_user_library(context)
    if library:
        browser_library = get_asset_browser_dir(context)

        # create cat.txt file
        cats_path = browser_library.joinpath("blender_assets.cats.txt")
        catalogs = {"ASSETS": "Assets", "ENVIRONMENTS": "Environments"}

        if not cats_path.exists():
            with open(cats_path, "w") as f:
                f.write("# This is an Asset Catalog Definition file for Blender.\n")
                f.write("#\n")
                f.write("# Empty lines and lines starting with `#` will be ignored.\n")
                f.write(
                    "# The first non-ignored line should be the version indicator.\n"
                )
                f.write(
                    '# Other lines are of the format "UUID:Path to Asset:Simple Catalog Name"\n'
                )
                f.write("\n")
                f.write("VERSION 1\n")
                f.write("\n")

                f.write(f"{default.GRASWALD_CATALOG_ID}:Graswald:Graswald\n")
                for cat in catalogs:
                    id = getattr(default, f"{cat}_CATALOG_ID")
                    f.write(f"{id}:Graswald/{catalogs[cat]}:Graswald-{catalogs[cat]}\n")


creating = False


@persistent
def create_library(self, Dephsgraph):
    prefs = get_preferences()
    if not prefs.enable_experimental_features:
        load_library()
        return

    global creating
    if creating:
        return

    browser_library = get_asset_browser_dir(bpy.context)
    if "Graswald" not in bpy.context.preferences.filepaths.asset_libraries.keys():
        creating = True
        bpy.ops.preferences.asset_library_add()
        new_library: UserAssetLibrary = (
            bpy.context.preferences.filepaths.asset_libraries[-1]
        )
        new_library.name = "Graswald"
        new_library.path = browser_library.as_posix()
        create_gscatter_asset_browser_entry()
        load_library(True)
        refresh_library()
        creating = False
    else:
        library = bpy.context.preferences.filepaths.asset_libraries["Graswald"]
        if library.path != browser_library.as_posix():
            library.path = browser_library.as_posix()
            create_gscatter_asset_browser_entry()
            load_library(True)
            refresh_library()


@persistent
def clear_graswald_duplicates(self, dephs):
    try:
        entry = next(
            (idx, ent)
            for idx, ent in enumerate(bpy.context.preferences.filepaths.asset_libraries)
            if ent.name.startswith("Graswald.")
        )
    except Exception:
        debug("No Duplicates Found.")
        return
    debug(f"Removing Graswald filepath duplicates {entry[1].name}")
    bpy.ops.preferences.asset_library_remove(index=entry[0])
    clear_graswald_duplicates(None, None)


@persistent
def check_gscatter_asset_browser_entry(self, context: bpy.types.Context):
    add_callback(create_gscatter_asset_browser_entry)


def register():
    bpy.app.handlers.load_post.append(check_gscatter_asset_browser_entry)
    bpy.app.handlers.load_post.append(clear_graswald_duplicates)
    bpy.app.handlers.load_post.append(create_library)


def unregister():
    bpy.app.handlers.load_post.remove(check_gscatter_asset_browser_entry)
    bpy.app.handlers.load_post.remove(clear_graswald_duplicates)
    bpy.app.handlers.load_post.remove(create_library)
