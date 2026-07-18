import json
import math
import os
import re
import subprocess
import zipfile
from glob import glob
from json import loads
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

import bpy

from ..utils.logger import debug

from ..utils.getters import get_asset_browser_dir, get_preferences
from . import default
from .schema import verify_asset, verify_environment

if TYPE_CHECKING:
    from ..common.props import WindowManagerProps
    from .props.library import LibraryWidget

# def system_library() -> Path:
#     return Path(__file__).resolve().parent.joinpath('library')


def user_library() -> Path:
    library_path = Path(get_preferences().t3dn_library).resolve()
    library_path.mkdir(parents=True, exist_ok=True)
    return library_path


def load_library(get_free_assets=False):
    """Load assets for the library."""
    all_products = list()
    all_assets = list()
    all_environments = list()
    all_tags = set()

    # library_path_internal = system_library()
    library_path_external = user_library()

    # product_paths_internal = list(glob(str(library_path_internal.joinpath('**', 'product.json')), recursive=True))
    product_paths_external = list(
        glob(str(library_path_external.joinpath("**", "product.json")), recursive=True)
    )

    new_assets = []

    for product_path in [] + product_paths_external:
        product_path = Path(product_path)

        try:
            product_data = loads(product_path.read_text())
        except json.decoder.JSONDecodeError:
            debug(f"GScatter:  Invalid JSON at {product_path}")
            continue

        # Verify product.json schema
        if not verify_asset(product_data) and not verify_environment(product_data):
            continue

        folder_name = product_path.parent.name
        # Check if the product is already loaded
        product_id = product_data.get("product_id")
        if product_id is None:
            product_id = product_path.parent.name
        asset_pattern = re.compile("([a-zA-Z0-9]*_[a-zA-Z0-9]*)")
        m = asset_pattern.match(product_id)

        is_old = False
        if m and product_data.get("asset_type") != "environment":
            folder_name = m.groups()[0]
            if folder_name in new_assets:
                continue
            new_assets.append(product_id)
        else:
            is_old = True

        if product_data.get("asset_type") == "environment":
            icon_path = product_data["preview"]
            icon_path = product_path.parent.joinpath(icon_path)

            for index, path in enumerate(product_data["blends"]):
                path = product_path.parent.joinpath(path)
                product_data["blends"][index] = str(path)

            product_data["previews"] = {
                "gallery": icon_path.as_posix(),
                "details": [icon_path.as_posix()],
            }

            all_environments.append(product_data)
            continue

        for author_data in product_data["authors"].values():
            icon_path = author_data["icon"]
            icon_path = product_path.parent.joinpath(icon_path)
            author_data["icon"] = str(icon_path)

        product_assets = []

        for asset_path in product_data["assets"]:
            asset_path = product_path.parent.joinpath(asset_path)

            if not asset_path.exists():
                debug(f"GScatter:  ASSET_META_NOT_FOUND: {asset_path.as_posix()} ")
                continue

            asset_data = loads(asset_path.read_text())

            # Check if asset is old and is already loaded
            if is_old and asset_data["name"] in [
                asset_data["name"] for asset_data in all_assets
            ]:
                continue

            author_id = asset_data["author"]
            author_data = product_data["authors"][author_id]
            asset_data["author"] = author_data

            gallery_path = asset_data["previews"]["gallery"]
            gallery_path = product_path.parent.joinpath(gallery_path)
            asset_data["previews"]["gallery"] = str(gallery_path)

            for index, path in enumerate(asset_data["previews"]["details"]):
                path = product_path.parent.joinpath(path)
                asset_data["previews"]["details"][index] = str(path)

            for index, path in enumerate(asset_data["blends"]):
                path = product_path.parent.joinpath(path)
                asset_data["blends"][index] = str(path)

            asset_data["asset_id"] = folder_name
            asset_data["product_name"] = product_data.get("name", "Unknown")

            all_assets.append(asset_data)
            product_assets.append(asset_data)
            all_tags.update(set(asset_data["tags"]))

    all_products = sorted(all_products, key=lambda data: data["name"])
    all_assets = sorted(all_assets, key=lambda data: data["name"])
    all_tags = sorted(list(all_tags))

    wm_props: "WindowManagerProps" = bpy.context.window_manager.gscatter
    library: "LibraryWidget" = wm_props.library
    library.load(
        {
            "products": all_products,
            "assets": all_assets,
            "tags": all_tags,
            "environments": all_environments,
        },
        get_free_assets,
    )


def draw_popup(
    self,
    context: bpy.types.Context,
    event: bpy.types.Event,
    width: int = 300,
    center: bool = False,
    dialog: bool = False,
):
    """
    Draw a popup aligned to the center of the cursor.

    Args:
        self: The operator calling this function
        context: The context from operator invoke.
        event: The event from operator invoke.
        width: The width of the popup to be drawn.
    """
    win_man = context.window_manager
    ui_scale = bpy.context.preferences.view.ui_scale

    x_loc = event.mouse_x
    y_loc = event.mouse_y

    if center:
        x_val, y_val = (context.window.width / 2), (context.window.height - 100)
    else:
        x_val, y_val = ((width / 2) * ui_scale), (5 * ui_scale)

    if dialog:
        context.window.cursor_warp(round(x_val), round(y_val))
        return_value = win_man.invoke_props_dialog(self, width=round(width))
    else:
        context.window.cursor_warp(round(x_loc - x_val), round(y_loc + y_val))
        return_value = win_man.invoke_popup(self, width=width)

    context.window.cursor_warp(round(x_loc), round(y_loc))

    return return_value


def calc_split_factor(width: int, sidebar_width: int) -> float:
    """
    Get the factor to use for splitting the popup into browser and sidebar.

    Args:
        width: The width of the full panel.
        sidebar_width: The width of the sidebar.

    Returns:
        The factor of the browser to the sidebar.
    """
    browser_width = width - sidebar_width
    return browser_width / width


def icon_scale_from_res(resolution: int) -> float:
    """
    Get a Blender icon scale value from a given resolution.

    Args:
        resolution: The image resolution to be converted.

    Returns:
        The Blender icon scale value of the resolution.
    """
    ui_scale = bpy.context.preferences.system.ui_scale
    adjustment = 2 / ui_scale if ui_scale < 1 else 0
    return 1 + (resolution - 12) / (20 + adjustment)


def tag_redraw():
    """Redraw every region in Blender."""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            for region in area.regions:
                region.tag_redraw()


def enable_wait_cursor():
    """Enable the loading wheel cursor."""
    bpy.context.window.cursor_modal_set("WAIT")


def disable_wait_cursor():
    """Disable the loading wheel cursor."""
    bpy.context.window.cursor_modal_restore()


def read_product_json(gscatter_path: Path = None, product_json_path=None):
    if product_json_path is None:
        with zipfile.ZipFile(gscatter_path) as zip_file:
            # Find the path to the product.json file inside the zip file
            for name in zip_file.namelist():
                if name.endswith("/product.json") and "/Assets/" not in name:
                    product_json_path = name
                    break

            if product_json_path is not None:
                with zip_file.open(product_json_path) as product_json_file:
                    # Load the contents of the product.json file
                    data = json.load(product_json_file)
            else:
                debug("Could not find product.json file in the zip file.")
                return None
    else:
        with open(product_json_path, "r") as product_json_file:
            # Load the contents of the product.json file
            data = json.load(product_json_file)

    return data


def get_asset_type(gscatter_path: Path = None, product_json_path=None) -> bool:
    data: dict | None = read_product_json(gscatter_path, product_json_path)
    if data is None:
        return "UNKNOWN"
    asset_type = data.get("asset_type")
    return asset_type.upper() if asset_type else "3D_PLANT"


def get_asset_type_from_asset_browser(asset):
    tags = []
    try:
        if asset.asset_data:
            tags = asset.asset_data.tags
    except AttributeError:
        if asset.metadata:
            tags = asset.metadata.tags

    for tag in tags:
        if tag.name == "asset_type:3D_PLANT":
            return "3D_PLANT"
        elif tag.name == "asset_type:ENVIRONMENT":
            return "ENVIRONMENT"
        elif tag.name == "asset_type:FREE_ASSET":
            return "FREE_ASSET"


def create_asset_browser_entry(
    context,
    name: str,
    product_data: dict,
    asset_type: str,
    asset_dir: Path,
    create_object_entry=False,
    create_lod_collection_entry=False,
    background=True,
):
    """create asset browser blend file"""
    # prefs = get_preferences()

    asset_browser_library = get_asset_browser_dir(context)

    blender_exec = Path(bpy.app.binary_path)
    script_path = (
        Path(__file__).parent.joinpath("asset_blend_file_creator.py").resolve()
    )
    script_path = str(script_path)

    if asset_type == "FREE_ASSET":
        asset_blend_path = asset_browser_library.joinpath(f"FREE_ASSET-{name}.blend")
    else:
        asset_blend_path = asset_browser_library.joinpath(f"{name}.blend")

    CATALOG = {
        "3D_PLANT": "Assets",
        "ENVIRONMENT": "Environments",
        "FREE_ASSET": "Free Assets",
    }

    catalog = CATALOG[asset_type]

    product_id = product_data.get("product_id", name)

    if asset_type == "FREE_ASSET":
        catalog_id = default.FREE_ASSET_CATALOG_ID
    else:
        catalog_id = str(uuid4())
        with open(asset_browser_library.joinpath("blender_assets.cats.txt"), "r+") as f:
            f.readlines()
            new_line = (
                f"{catalog_id}:Graswald/{catalog}/{product_id}:{catalog}-{product_id}\n"
            )
            f.write(new_line)

    if asset_blend_path.exists():
        return None

    variants = []
    if asset_type == "3D_PLANT":
        for meta in product_data.get("assets", []):
            meta_file = asset_dir.joinpath(meta)
            meta_f = open(meta_file, "r")
            meta_data = json.load(meta_f)
            meta_f.close()
            lod_catalog_ids = {}
            variant_catalog_id = str(uuid4())
            variant = meta_data["configurator"]["attributes"].get(
                "Variant", meta_data["configurator"]["attributes"].get("Life Cycle")
            )
            debug(variant)

            with open(
                asset_browser_library.joinpath("blender_assets.cats.txt"), "r+"
            ) as f:
                f.readlines()
                new_lines = f"{variant_catalog_id}:Graswald/{catalog}/{product_id}/{variant}:{product_id}-{variant}\n"
                for lod in meta_data["configurator"]["properties"]["Level Of Detail"]:
                    lod_catalog_id = str(uuid4())
                    if create_object_entry or create_lod_collection_entry:
                        new_lines += f"{lod_catalog_id}:Graswald/{catalog}/{product_id}/{variant}/LOD{lod}:{variant}-LOD{lod}\n"
                    lod_catalog_ids["lod" + lod] = lod_catalog_id
                f.write(new_lines)

            variants.append(
                {
                    "name": meta_data["name"],
                    "description": meta_data["description"],
                    "author": meta_data["author"],
                    "id": variant,
                    "lod_catalog_ids": lod_catalog_ids,
                    "variant_catalog_id": variant_catalog_id,
                    "preview": asset_dir.joinpath(
                        meta_data["previews"]["gallery"]
                    ).as_posix(),
                }
            )

    environment_preview = (
        asset_dir.joinpath(product_data.get("preview"))
        if asset_type == "ENVIRONMENT"
        else product_data.get("preview")
        if asset_type == "FREE_ASSET"
        else ""
    )

    data_blend_path = asset_dir.joinpath("data", "data.blend")
    if data_blend_path.exists():
        pass
    else:
        blend_filename = name.lower().replace(" ", "")
        data_blend_path = asset_dir.joinpath("data", f"{blend_filename}.blend")

    blender_cmd = [
        blender_exec,
        "-b",
        "-P",
        script_path,
        "--",
        data_blend_path,
        asset_blend_path,
        product_data["name"],
        product_id,
        catalog_id,
        str(variants),
        asset_type,
        environment_preview,
        str(create_object_entry),
        str(create_lod_collection_entry),
    ]
    process = subprocess.call(blender_cmd)

    # process = subprocess.Popen(blender_cmd)
    return process, asset_blend_path, catalog_id


def get_catalog_name(id: str):
    asset_browser_library = get_asset_browser_dir()
    catalog_path = asset_browser_library.joinpath("blender_assets.cats.txt")
    with open(catalog_path, "r+") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(id):
                name = line.split("/")[-1].split(":")[0]
                return name


def clear_free_assets_entries():
    prefix = "FREE_ASSET-"
    asset_browser_library = get_asset_browser_dir().as_posix()
    for filename in os.listdir(asset_browser_library):
        if filename.startswith(prefix):
            file_path = os.path.join(asset_browser_library, filename)
            os.remove(file_path)
            debug(f"GScatter: Deleted file: {file_path}")

    asset_list_path = get_asset_browser_dir().joinpath("free_assets.json")
    if asset_list_path.exists():
        os.remove(asset_list_path)


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
