import os
import shutil
import json
import threading
from functools import partial
from pathlib import Path
from zipfile import ZipFile, is_zipfile
import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty
from bpy.types import Context, Operator
from bpy_extras.io_utils import ImportHelper
from .. import utils
from .. import default
from ... import icons
from ..asset_browser import refresh_library, set_catalog_id
from ..utils import create_asset_browser_entry
from ...effects.store import effectstore, effectpresetstore
from ...scatter.store import scattersystempresetstore
from ...utils.getters import get_asset_browser_dir, get_user_library
from ...utils.logger import debug, success
from ...slow_task_manager.scopped_slow_task import StartSlowTask
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..props.library import LibraryWidget


class RefreshLibraryOperator(Operator):
    bl_idname = "gscatter.refresh_library"
    bl_label = "Refresh Library"
    # bl_description = ("Refresh contents from the library folder\nCtrl click to reload free assets")
    bl_options = {"REGISTER", "INTERNAL"}

    load_free_assets: BoolProperty(default=False)

    tooltip: StringProperty()

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip

    def execute(self, context: Context):
        utils.load_library(self.load_free_assets)
        self.report({"INFO"}, "Refreshed library")
        return {"FINISHED"}


class InstallAssetsOperator(Operator, ImportHelper):
    bl_idname = "gscatter.install_assets"
    bl_label = "Install Assets"
    bl_description = "Install assets from a gscatter file"
    bl_options = {"REGISTER", "INTERNAL"}

    filter_glob: StringProperty(default="*.gscatter;*.zip", options={"HIDDEN"})
    files: CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )
    directory: StringProperty(
        subtype="DIR_PATH",
    )

    def execute(self, context: Context):
        library_path = utils.user_library()

        if not library_path.is_dir():
            self.report({"INFO"}, f'Library "{library_path}" does not exist')
            return {"CANCELLED"}

        directory = self.directory
        total = len(self.files)
        total_failed: int = 0
        with StartSlowTask("Installing Assets", total) as task:
            for i in range(total):
                file_elem = self.files[i]
                task.set_progress(i)
                task.set_progress_text("Installing: " + file_elem.name)
                task.refresh()

                file_path = Path(directory, file_elem.name)

                if not file_path.is_file():
                    self.report({"ERROR"}, f'File "{file_path}" does not exist')
                    total_failed += 1
                    continue

                if not is_zipfile(file_path):
                    self.report(
                        {"ERROR"}, f'File "{file_path}" is not a valid gscatter file'
                    )
                    total_failed += 1
                    continue

                asset_type = utils.get_asset_type(file_path)
                if asset_type == "UNKNOWN":
                    self.report(
                        {"ERROR"}, f'File "{file_path}" is not a valid gscatter file'
                    )
                    total_failed += 1
                    continue

                if asset_type == "ENVIRONMENT":
                    extract_dir = library_path.joinpath("Environments")
                else:
                    extract_dir = library_path.joinpath("Assets")

                extract_dir.mkdir(parents=True, exist_ok=True)

                with ZipFile(file_path, "r") as file:
                    folder_names = [
                        name
                        for name in file.namelist()
                        if name.endswith("/") and name.count("/") == 1
                    ]
                    file.extractall(extract_dir)

                if asset_type == "ENVIRONMENT":
                    continue

                for asset in folder_names:
                    asset_dir = extract_dir.joinpath(asset)

                    # Install effect/presets
                    """if file_elem.name.endswith(".gscatter"):
                        asset_dir = extract_dir.joinpath(
                            file_elem.name.removesuffix(".gscatter")
                        )
                    else:
                        asset_dir = extract_dir.joinpath(
                            file_elem.name.removesuffix(".zip")
                        )"""

                    files = os.listdir(asset_dir.joinpath("meta"))
                    variants = []

                    for file in files:
                        file_path = asset_dir.joinpath("meta", file)

                        with open(file_path, "r") as f:
                            data = json.load(f)
                            variant = data["name"]
                            variants.append({"name": variant, "tags": data["tags"]})

                    data = {"data": variants}

                    # Check for effects.json and if found install it
                    effect_json = asset_dir.joinpath("effects.json")
                    if effect_json.exists():
                        effectstore.merge(effect_json.as_posix(), "user")

                    # Check for effect_presets.json and if found install the presets
                    effect_presets_json = asset_dir.joinpath("effect_presets.json")
                    if effect_presets_json.exists():
                        effectpresetstore.merge(effect_presets_json.as_posix(), "user")

                    # Check for system_presets.json and if found install the system_presets
                    system_presets_json = asset_dir.joinpath("system_presets.json")
                    if system_presets_json.exists():
                        scattersystempresetstore.merge(
                            system_presets_json.as_posix(), "user"
                        )

                    # Check if icons folder exists
                    icons_folder = asset_dir.joinpath("icons")
                    user_icons_folder = library_path.joinpath("icons")
                    user_icons_folder.mkdir(exist_ok=True)
                    if icons_folder.exists():
                        shutil.copytree(
                            icons_folder, user_icons_folder, dirs_exist_ok=True
                        )
                        icons.load_user_icons()

        utils.load_library()

        def show_message():
            bpy.ops.gscatter.popup_message(
                "INVOKE_DEFAULT", message="Asset Installed", width=200
            )

        if total - total_failed > 0:
            bpy.app.timers.register(show_message, first_interval=0.1)
            self.report({"INFO"}, f"Installed: {total-total_failed} assets. ")
        else:
            self.report({"ERROR"}, f"Installation failed for {total_failed} assets. ")

        return {"FINISHED"}


class AssetBrowserInstallAssetsOperator(Operator, ImportHelper):
    bl_idname = "gscatter.asset_browser_install_assets"
    bl_label = "Install Assets"
    bl_description = "Install graswald assets"
    bl_options = {"REGISTER", "INTERNAL"}

    filter_glob: StringProperty(default="*.gscatter;*.zip;", options={"HIDDEN"})
    files: CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )
    directory: StringProperty(
        subtype="DIR_PATH",
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    create_object_entry: BoolProperty(
        description="Will Mark every model as Asset.", default=False
    )
    create_lod_collection_entry: BoolProperty(
        description="Will mark every LOD collection as Asset aswell.", default=False
    )

    def draw(self, context):
        pass

    def execute(self, context: Context):
        directory = self.directory
        catalog_id = None

        files = [file for file in self.files if Path(directory, file.name).is_file()]
        total = len(files)
        total_failed: int = 0

        if total == 0:
            self.report({"ERROR"}, "No files selected.")

        # user_asset_dir = get_user_assets_dir(context)
        # asset_browser_library = get_asset_browser_dir(context)
        library_path = get_user_library(context)
        if not library_path.is_dir():
            self.report(
                {"ERROR"},
                f'Library "{library_path}" does not exist. You might try restarting Blender.',
            )
            return {"CANCELLED"}

        operator = self
        with StartSlowTask("Installing Assets", total) as task:
            for i in range(total):
                file_elem = files[i]
                task.set_progress(i)
                task.set_progress_text("Installing: " + file_elem.name)
                task.refresh()

                file_path = Path(directory, file_elem.name)

                if not is_zipfile(file_path) or file_path.suffix not in [
                    ".gscatter",
                    ".zip",
                ]:
                    operator.report(
                        {"ERROR"}, f'File "{file_path}" is not a valid gscatter file'
                    )
                    total_failed += 1
                    continue

                asset_type = utils.get_asset_type(file_path)

                if asset_type == "UNKNOWN":
                    operator.report(
                        {"ERROR"}, f'File "{file_path}" is not a valid gscatter file'
                    )
                    total_failed += 1
                    continue

                if asset_type == "ENVIRONMENT":
                    extract_dir = library_path.joinpath("Environments")
                else:
                    extract_dir = library_path.joinpath("Assets")

                extract_dir.mkdir(parents=True, exist_ok=True)

                with StartSlowTask("Extracting Asset", 1) as extract_task:
                    extract_task.set_progress(0)
                    extract_task.set_progress_text("Extracting: " + file_elem.name)
                    extract_task.refresh()
                    with ZipFile(file_path, "r") as file:
                        folder_names = [
                            name
                            for name in file.namelist()
                            if name.endswith("/") and name.count("/") == 1
                        ]
                        file.extractall(extract_dir)

                with StartSlowTask(
                    "Installing Asset", len(folder_names)
                ) as extract_task:
                    total += len(folder_names) - 1
                    count = 0
                    for folder in folder_names:
                        count += 1
                        extract_task.set_progress(count)
                        extract_task.set_progress_text("Installing: " + folder)
                        extract_task.refresh()

                        asset_dir = extract_dir.joinpath(folder)
                        product_json = asset_dir.joinpath("product.json")

                        f = open(product_json, "r")
                        product_data = json.load(f)
                        f.close()
                        name = name = product_data.get("name", "")
                        result = create_asset_browser_entry(
                            context,
                            name,
                            product_data,
                            asset_type,
                            asset_dir,
                            self.create_object_entry,
                            self.create_lod_collection_entry,
                        )
                        if result:
                            process, asset_blend_path, catalog_id = result

                        # Check for effects.json and if found install it
                        effect_json = asset_dir.joinpath("effects.json")
                        if effect_json.exists():
                            debug("Found effects.json file")
                            effectstore.merge(effect_json.as_posix(), "user")

                        # Check for effect_presets.json and if found install the presets
                        effect_presets_json = asset_dir.joinpath("effect_presets.json")
                        if effect_presets_json.exists():
                            debug("Found effect_presets.json file")
                            effectpresetstore.merge(
                                effect_presets_json.as_posix(), "user"
                            )

                        # Check for system_presets.json and if found install the system_presets
                        system_presets_json = asset_dir.joinpath("system_presets.json")
                        if system_presets_json.exists():
                            debug("Found system_presets.json file")
                            scattersystempresetstore.merge(
                                system_presets_json.as_posix(), "user"
                            )

                        # Check if icons folder exists
                        icons_folder = asset_dir.joinpath("icons")
                        user_icons_folder = library_path.joinpath("icons")
                        user_icons_folder.mkdir(exist_ok=True)
                        if icons_folder.exists():
                            shutil.copytree(
                                icons_folder, user_icons_folder, dirs_exist_ok=True
                            )
                            icons.load_user_icons()

        if catalog_id:
            bpy.app.timers.register(
                partial(set_catalog_id, catalog_id), first_interval=1
            )
        bpy.app.timers.register(utils.load_library, first_interval=1)
        bpy.app.timers.register(refresh_library, first_interval=1)

        # try:
        #     os.system("cls")
        # except Exception:
        #     ...
        def show_message():
            bpy.ops.gscatter.popup_message(
                "INVOKE_DEFAULT",
                message=f"Installed: {total-total_failed} assets. ",
                width=200,
            )

        if total - total_failed > 0:
            bpy.app.timers.register(show_message, first_interval=0.1)
            self.report({"INFO"}, f"Installed: {total-total_failed} assets. ")
        else:
            self.report({"ERROR"}, f"Installed: {total-total_failed} assets.")

        area = context.area

        def refresh():
            area.tag_redraw()
            # os.system("cls")
            success(f":tada: Installed {total-total_failed} assets in asset browser")
            success(
                "Minimise this window, or close it using menu: Window > Toggle System Console"
            )

        bpy.app.timers.register(refresh, first_interval=0.1)
        return {"FINISHED"}


class AssetBrowserInstallOperatorPropsPanel(bpy.types.Panel):
    bl_idname = "GSCATTER_PT_AssetBrowserInstallProps"
    bl_label = "Install Settings"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "GSCATTER_OT_asset_browser_install_assets"

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(
            data=operator, property="create_object_entry", text="Create Object Entries"
        )
        layout.prop(
            data=operator,
            property="create_lod_collection_entry",
            text="Create LOD Entries",
        )


class InstallOldAssetList(bpy.types.UIList):
    bl_idname = "GSCATTER_UL_scatter_old_assets_reinstall"

    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):
        row = layout.row()
        row.prop(item, "select", text="")
        row.label(text=item.name)


class OldAssetItem(bpy.types.PropertyGroup):
    name: StringProperty()
    target: StringProperty()
    id: StringProperty()
    select: BoolProperty(default=True, name="Select")


class SyncInstalledAssetsOperator(Operator):
    bl_idname = "gscatter.sync_installed_assets"
    bl_label = "Sync Installed Assets"
    bl_description = "Sync old installed assets with the new GScatter Asset Browser."

    def update_select_all(self, context):
        for asset in self.assets:
            asset.select = self.select_all

    index: IntProperty()
    assets: CollectionProperty(type=OldAssetItem)
    select_all: BoolProperty(name="Select All", default=True, update=update_select_all)
    create_object_entry: BoolProperty("Create Object Entry", default=False)
    create_lod_collection_entry: BoolProperty("Create LOD Collection", default=False)

    _timer = None
    _task = None
    _thread = None
    _stop_flag = threading.Event()

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.scale_y = 0.7

        col.label(text="Select the assets you want to sync.")
        col.separator()
        col.label(text="Below are list of installed assets which are not in sync")
        col.label(text="with the new GScatter Asset Browser. ")

        layout.prop(self, "select_all", text="Select All")

        layout.template_list(
            InstallOldAssetList.bl_idname,
            "",
            self,
            "assets",
            self,
            "index",
            rows=6,
        )

        layout.prop(self, "create_object_entry", text="Create Entry for each Object")
        layout.prop(self, "create_lod_collection_entry", text="Create LOD Collections")

    def invoke(self, context, event):
        self.assets.clear()

        library: "LibraryWidget" = context.window_manager.gscatter.library
        asset_browser_library = get_asset_browser_dir(context)
        cats_path = asset_browser_library.joinpath("blender_assets.cats.txt")

        if not cats_path.exists():
            return {"CANCELLED"}

        with open(cats_path, "r+") as f:
            lines = f.readlines()

        not_availalble = set()

        for asset in list(library.assets) + list(library.environments):
            available = False
            for line in lines:
                name = getattr(asset, "product_name", asset.name)
                if (
                    asset.asset_id in line
                    or asset.name in line
                    or name in line
                    or asset.name in line
                ):
                    available = True
                    break

            if not available and asset.asset_id not in not_availalble:
                new = self.assets.add()
                name = getattr(asset, "product_name", asset.name)
                new.name = name
                new.target = repr(asset)
                new.id = asset.asset_id
                not_availalble.add(asset.asset_id)

        return context.window_manager.invoke_props_dialog(self, width=350)

    def execute(self, context):
        selected = [asset for asset in self.assets if asset.select]
        total = len(selected)
        if total == 0:
            self.report({"ERROR"}, "No assets selected")
            return {"CANCELLED"}

        library: "LibraryWidget" = context.window_manager.gscatter.library
        library.syncing_assets = True
        library.syncing_assets_progress = 0
        wm = context.window_manager
        wm.progress_begin(0, 100)
        self.report({"INFO"}, "Syncing Assets in background.")

        # Start the background task
        self._thread = threading.Thread(
            target=self.run_background_task_with_progress, args=(context,)
        )
        self._thread.start()

        self._timer = wm.event_timer_add(0.1, window=context.window)

        # def show_message():
        #     bpy.ops.gscatter.popup_message("INVOKE_DEFAULT", message="Syncing Assets in Background.", width=200)
        # bpy.app.timers.register(show_message, first_interval=0.1)

        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "TIMER":
            if not self._thread.is_alive():
                context.window_manager.event_timer_remove(self._timer)
                library: "LibraryWidget" = context.window_manager.gscatter.library
                library.syncing_assets = False
                library.syncing_assets_progress = 100
                refresh_library()
                return {"FINISHED"}
        return {"PASS_THROUGH"}

    def run_background_task_with_progress(self, context: Context):
        selected = [asset for asset in self.assets if asset.select]
        total = len(selected)
        processed_files = 0

        for i in range(total):
            processed_files += 1
            progress = (processed_files / total) * 100
            library: "LibraryWidget" = context.window_manager.gscatter.library
            library.syncing_assets_progress = progress

            asset_data = selected[i]
            asset: "OldAssetItem" = eval(asset_data.target)
            # name = getattr(asset, "product_name", asset.name)
            asset_dir = Path(asset.blends[0].name).parent.parent

            product_json = asset_dir.joinpath("product.json")

            f = open(product_json, "r")
            product_data = json.load(f)
            f.close()

            asset_type = utils.get_asset_type(product_json_path=product_json)
            create_asset_browser_entry(
                context,
                product_data.get("name", asset_dir.name),
                product_data,
                asset_type,
                asset_dir,
                self.create_object_entry,
                self.create_lod_collection_entry,
            )
            context.window_manager.progress_update((processed_files / total) * 100)

            refresh_library()

        # def show_message():
        #     bpy.ops.gscatter.popup_message("INVOKE_DEFAULT", message=f"Synced {total} old assets. ", width=200)
        # bpy.app.timers.register(show_message, first_interval=0.1)

        self.report({"INFO"}, message=f"Installed {total} assets in asset browser")

    def cancel(self, context):
        self._stop_flag.set()
        if self._thread:
            if self._thread.is_alive():
                self._thread.join()
        context.window_manager.event_timer_remove(self._timer)
        context.window_manager.progress_end()
        library: "LibraryWidget" = context.window_manager.gscatter.library
        library.syncing_assets = False
        library.syncing_assets_progress = 0
        return {"CANCELLED"}

    def sync_assets_in_background(self, context: Context):
        selected = [asset for asset in self.assets if asset.select]
        total = len(selected)
        with StartSlowTask("Installing Assets", total) as task:
            for i in range(total):
                asset_data = selected[i]
                asset = eval(asset_data.target)
                name = getattr(asset, "product_name", asset.name)
                task.set_progress(i)
                task.set_progress_text(
                    f"Installing: {name}\nWarning, this operation will take a few minutes."
                )
                task.refresh()

                asset_dir = Path(asset.blends[0].name).parent.parent

                product_json = asset_dir.joinpath("product.json")

                f = open(product_json, "r")
                product_data = json.load(f)
                f.close()

                asset_type = utils.get_asset_type(product_json_path=product_json)
                create_asset_browser_entry(
                    context,
                    product_data.get("name", asset_dir.name),
                    product_data,
                    asset_type,
                    asset_dir,
                    self.create_object_entry,
                    self.create_lod_collection_entry,
                )

            refresh_library()

        # def show_message():
        #     bpy.ops.gscatter.popup_message("INVOKE_DEFAULT",
        #                                    message=f"Synced {total} old assets. ",
        #                                    width=200)
        # bpy.app.timers.register(show_message, first_interval=0.1)

        self.report({"INFO"}, message=f"Installed {total} assets in asset browser")
        return {"FINISHED"}


class DeleteCatalogEntryOperator(Operator):
    bl_idname = "gscatter.delete_catalog_entry"
    bl_label = "Delete Asset from Asset Browser"

    catalog_id: StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        asset_browser_dir = get_asset_browser_dir()
        catalog_path = asset_browser_dir.joinpath("blender_assets.cats.txt")
        with open(catalog_path, "r") as f:
            the_lines = f.readlines()
            try:
                line = next(
                    line for line in the_lines if line.startswith(self.catalog_id)
                )
            except Exception:
                self.report({"INFO"}, "Selected Catalog cannot be deleted. Cancelled")
                return {"CANCELLED"}
            if "Graswald" not in line:
                self.report({"INFO"}, "Selected Catalog cannot be deleted. Cancelled")
                return {"CANCELLED"}

            if (
                self.catalog_id == default.ASSETS_CATALOG_ID
                or self.catalog_id == default.ENVIRONMENTS_CATALOG_ID
                or self.catalog_id == default.FREE_ASSET_CATALOG_ID
            ):
                self.report({"INFO"}, "Selected Catalog cannot be deleted. Cancelled")
                return {"CANCELLED"}
            catalog_name = line.split("Assets/")[-1].split(":")[0].split("/")[0]
            lines = [line for line in the_lines if catalog_name not in line]

        with open(catalog_path, "w") as f:
            f.writelines(lines)

        blend_path = asset_browser_dir.joinpath(catalog_name + ".blend")
        if blend_path.exists():
            os.remove(blend_path)
        bpy.app.timers.register(refresh_library, first_interval=1)
        return {"FINISHED"}


class RefreshAssetBrowserOperator(Operator):
    bl_idname = "gscatter.refresh_asset_browser"
    bl_label = "Assets installed. Refresh Asset Browser"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        refresh_library()
        return {"FINISHED"}


classes = (
    RefreshLibraryOperator,
    InstallAssetsOperator,
    AssetBrowserInstallAssetsOperator,
    AssetBrowserInstallOperatorPropsPanel,
    InstallOldAssetList,
    OldAssetItem,
    SyncInstalledAssetsOperator,
    DeleteCatalogEntryOperator,
    RefreshAssetBrowserOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
