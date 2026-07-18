import json
import os
import shutil
import tempfile
import threading
from typing import Union
from zipfile import ZipFile

import bpy
import requests
from bpy.props import (
    StringProperty,
    FloatProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
)
from bpy.types import OperatorProperties, UILayout

from ...utils.logger import error, info, success

from ...utils import wrap_text
from ...utils.getters import get_asset_browser_dir, get_preferences, get_user_library
from .. import previews, utils
from ..ops.misc import DummyOperator, SelectItemOperator
from ..ops.popup import OpenPreviewPopup
from .base import BaseWidget

tmp_dir = tempfile.gettempdir()

FREE_ASSETS_JSON_LIST_URL = "https://asset-downloads.gscatter.com/file-downloads/gscatter/free-assets/asset-list"

ASSET = {"3D_PLANT": "Asset", "ENVIRONMENT": "Environment"}


class FreeAssetWidget(BaseWidget):
    name: StringProperty(name="Name")
    icon: StringProperty(name="Icon")
    description: StringProperty(name="Description")
    asset_id: StringProperty(name="Asset ID")
    asset_type: EnumProperty(
        items=[
            ("3D_PLANT", "Plants", ""),
            ("ENVIRONMENT", "Environment", ""),
        ]
    )
    tags: CollectionProperty(name="Tags", type=BaseWidget)
    select: BoolProperty()
    expanded: BoolProperty(default=False)
    url: StringProperty(name="URL")
    total_size: StringProperty(name="Size")
    progress: FloatProperty(name="Progress", min=0, max=100, subtype="PERCENTAGE")
    downloading: BoolProperty()
    installing: BoolProperty()
    cancel_download: BoolProperty()

    def update_cancel(self, context):
        if self.cancel_download:
            self.downloading = False
            self.progress = 0

    def load(self, data: dict, create_entry=True):
        prefs = get_preferences()
        self.name = data.get("name", "")
        self.url = data.get("url", "")
        self.asset_id = data.get("asset_id", "")
        self.description = data.get("description", "")
        self.asset_type = data.get("asset_type", "3D_PLANT")

        library_path = get_user_library(bpy.context)
        user_icons_folder = library_path.joinpath("icons")
        user_icons_folder.mkdir(exist_ok=True)
        icon = user_icons_folder.joinpath(self.asset_id + ".bip")
        if icon.exists():
            self.icon = icon.as_posix()
            image_path = icon.as_posix()
        else:
            image_path = download_image(data.get("icon", ""), self.asset_id)
            self.icon = image_path.as_posix()

        if create_entry and prefs.enable_experimental_features:
            return True

    def draw_gallery(self, layout: UILayout):
        box = layout.box()
        preview = previews.get(self.icon)
        box.template_icon(
            icon_value=preview.icon_id, scale=utils.icon_scale_from_res(173)
        )
        row = layout.row(align=True)
        row.scale_y = 1.6
        library = self.parent
        op = row.operator(
            SelectItemOperator.bl_idname,
            text=self.name,
            depress=self.select,
            icon="CHECKMARK" if library.get_asset(self.asset_id) else "NONE",
        )
        op.target, op.deselect = repr(self), False
        # self.previews.draw_gallery(box)

    def draw_compact(self, layout: UILayout):
        library = self.parent
        if self.asset_type == "3D_PLANT" and library.get_asset(self.asset_id):
            return
        elif self.asset_type == "ENVIRONMENT" and library.get_environment_by_id(
            self.asset_id
        ):
            return
        elif self.asset_type == "ENVIRONMENT" and library.get_environment_by_name(
            self.name
        ):
            return

        col = layout.column(align=True)
        col.box().prop(
            self,
            "expanded",
            toggle=True,
            text=self.name + f" - [{ASSET[self.asset_type]}]",
            emboss=False,
            icon="TRIA_RIGHT" if not self.expanded else "TRIA_DOWN",
        )
        if self.expanded:
            self.draw_details(col.box())

    def draw_details(self, layout: UILayout):
        main_col = layout.column(align=True)

        box = main_col.box()
        preview = previews.get(self.icon)

        box.template_icon(
            icon_value=preview.icon_id, scale=utils.icon_scale_from_res(250)
        )

        row = main_col.box().row()
        row.operator(
            DummyOperator.bl_idname, text=self.name, emboss=False, depress=True
        )
        row.operator(
            OpenPreviewPopup.bl_idname, text="", icon="SEQ_PREVIEW"
        ).icon_id = repr(preview.icon_id)

        box = main_col.box()
        text_col = box.column(align=True)
        text_col.scale_y = 0.8
        for text in wrap_text(self.description, bpy.context.region.width):
            text_col.label(text=text)

        box = main_col.box()
        box.label(text=f"Type: {ASSET[self.asset_type]}")

        main_col.separator()
        col = main_col.column()
        col.scale_y = 2.0
        library = self.parent

        if not self.downloading:
            if self.asset_type == "3D_PLANT" and library.get_asset(self.asset_id):
                col.operator(
                    DummyOperator.bl_idname,
                    text="Asset is Installed.",
                    emboss=False,
                    depress=True,
                )
            elif self.asset_type == "ENVIRONMENT" and library.get_environment_by_id(
                self.asset_id
            ):
                col.operator(
                    DummyOperator.bl_idname,
                    text="Asset is Installed.",
                    emboss=False,
                    depress=True,
                )
            else:
                if library.loading_free_assets:
                    c = col.column()
                    c.enabled = False
                    c.scale_y = 0.5
                    c.label(text="Cannot download while assets are loading.")
                op: OperatorProperties = col.operator(
                    DownloadFreeAssetOperator.bl_idname, text="Download"
                )
                op.target = repr(self)
        else:
            row = col.row()
            row.enabled = False

            if not self.installing:
                row.prop(
                    self, "progress", slider=True, text=f"Downloading {self.total_size}"
                )
                row = col.row()
                row.prop(
                    self,
                    "cancel_download",
                    text="Cancel Download",
                    toggle=True,
                    emboss=False,
                )
            else:
                row.operator(
                    DummyOperator.bl_idname,
                    text="Installing Asset...",
                    emboss=True,
                    depress=True,
                )


class DownloadFreeAssetOperator(bpy.types.Operator):
    bl_idname = "gscatter.download_free_asset"
    bl_label = "Download"
    bl_description = "Download Asset"

    target: StringProperty()  # type: ignore

    @classmethod
    def poll(cls, context):
        library = context.window_manager.gscatter.library
        return not library.loading_free_assets

    def execute(self, context):
        asset: FreeAssetWidget = eval(self.target)
        temp_dir = tempfile.mkdtemp()
        filename = os.path.basename(asset.url)
        dest_url = os.path.join(temp_dir, filename)

        asset.installing = False
        asset.cancel_download = False

        if asset.downloading:
            self.report({"WARNING"}, message="Already Downloading. Cancelled.")
            return {"CANCELLED"}

        area = context.area

        def refresh():
            area.tag_redraw()
            if asset.downloading:
                return 1

        def show_message():
            bpy.ops.gscatter.popup_message(
                "INVOKE_DEFAULT", message="Asset Installed", width=200
            )

        def on_download_complete():
            library_path = utils.user_library()
            if asset.asset_type == "ENVIRONMENT":
                extract_dir = library_path.joinpath("Environments")
            else:
                extract_dir = library_path.joinpath("Assets")

            extract_dir.mkdir(parents=True, exist_ok=True)

            files = os.listdir(extract_dir)

            with ZipFile(dest_url, "r") as file:
                file.extractall(extract_dir)

            prefs = get_preferences()
            if prefs.enable_experimental_features:
                new_files = os.listdir(extract_dir)
                try:
                    asset_folder = next(file for file in new_files if file not in files)
                except Exception:
                    asset_folder = asset.name

                product_json = extract_dir.joinpath(asset_folder, "product.json")
                asset_dir = extract_dir.joinpath(asset_folder)

                f = open(product_json, "r")
                product_data = json.load(f)
                f.close()
                utils.create_asset_browser_entry(
                    context,
                    product_data.get("name", asset.name),
                    product_data,
                    asset.asset_type.upper(),
                    asset_dir,
                )
                # debug(result)
            bpy.app.timers.register(function=show_message, first_interval=0.5)
            asset.downloading = False
            asset.progress = 0
            asset.installing = False
            utils.load_library()

        def on_progress():
            refresh()

        def download() -> None:
            asset.downloading = True
            bpy.app.timers.register(function=refresh)
            download_file(asset, asset.url, dest_url, on_download_complete, on_progress)

        thread = threading.Thread(target=download)
        thread.start()
        if not thread.is_alive():
            thread.join()
        return {"FINISHED"}


def requestdownloadUrl(url: str):
    response = requests.get(url, headers={}, stream=True)
    response.raise_for_status()  # Raise an exception if the request was not successful
    if "application/json" not in [response.headers.get("content-type")]:
        return response
    json_data = response.json()
    if "data" not in json_data.keys():
        return response

    if "downloadUrl" in json_data["data"].keys():
        url = json_data["data"]["downloadUrl"]
        response = requests.get(url, headers={}, stream=True)
        response.raise_for_status()  # Raise an exception if the request was not successful
        return response

    return response


def download_image(url: str, asset_id: str):
    library_path = get_user_library(bpy.context)
    user_icons_folder = library_path.joinpath("icons")
    temp_dir = tempfile.mkdtemp()
    filename: str = os.path.basename(url)
    temp_path = os.path.join(temp_dir, filename)
    try:
        response = requestdownloadUrl(url)
        with open(temp_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
    except requests.exceptions.RequestException as e:
        error(e, "Error occurred while downloading file")
        ...

    # urllib.request.urlretrieve(url, temp_path)

    final_path = user_icons_folder.joinpath(asset_id + ".bip")
    shutil.copyfile(temp_path, final_path)
    return final_path


def download_file(
    asset: FreeAssetWidget, url, destination, on_download_complete_handler, on_progress
):
    asset.cancel_download = False

    try:
        response = requestdownloadUrl(url)
        response.raise_for_status()  # Raise an exception if the request was not successful

        total_size = int(response.headers.get("content-length", 0))
        asset.total_size = utils.convert_size(total_size)
        asset.progress = 0  # Reset progress to 0

        with open(destination, "wb") as file:
            cur = 1
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
                cur += len(chunk)
                if total_size > 0 and cur > 0:
                    asset.progress = (cur / total_size) * 100
                # on_progress()
                if asset.cancel_download:
                    asset.downloading = False
                    return False
        success("Download complete!")
        asset.installing = True
        on_download_complete_handler()
    except requests.exceptions.RequestException as e:
        error(e, "Error occurred while downloading file")
        asset.installing = False
        asset.downloading = False


def get_free_assets_list(callback, on_done) -> Union[dict, None]:
    def get_data():
        try:
            response = requestdownloadUrl(FREE_ASSETS_JSON_LIST_URL)
            data = response.json()
            # debug(data)

            user_library = get_asset_browser_dir()
            asset_list_path = user_library.joinpath("free_assets.json")
            old_data = {}
            if asset_list_path.exists():
                f = open(asset_list_path, "r")
                old_data = json.load(f)
                f.close()
            create_entry = False
            if data != old_data:
                info("GScatter: New Free Assets available...loading")
                f = open(asset_list_path, "w")
                f.write(json.dumps(data))
                f.close()
                create_entry = True
            if callback is not None:
                callback(data, create_entry)
            if on_done is not None:
                on_done()
        except requests.exceptions.RequestException as e:
            error(e, "Error occurred while downloading file")
            ...

    thread = threading.Thread(target=get_data)
    thread.start()
    if not thread.is_alive():
        thread.join()


classes = (
    FreeAssetWidget,
    DownloadFreeAssetOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
