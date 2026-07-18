import json
import math
from typing import Union

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import Context, UILayout
from bpy_extras import asset_utils

from ... import icons
from ...common.props import WindowManagerProps
from ...environment.ops import AddEnvironmentOperator
from ...scatter.store import scattersystempresetstore
from ...utils import wrap_text
from ...utils.getters import (
    get_allow_networking,
    get_asset_browser_dir,
    get_preferences,
)
from ...utils.logger import debug, error
from .. import previews, utils
from ..configurators import modules
from ..ops.install import InstallAssetsOperator, RefreshLibraryOperator
from ..ops.misc import ClearTagsOperator, DummyOperator
from ..ops.page import (
    ScrollPageLeftOperator,
    ScrollPageRightOperator,
    SelectPageOperator,
)
from ..ops.popup import FilterPopup
from ..ops.scatter import AddToSceneOperator, ScatterSelectedOperator
from ..utils import get_asset_type_from_asset_browser
from .asset import AssetWidget
from .base import BaseWidget
from .environment import EnvironmentWidget
from .free_assets import FreeAssetWidget, get_free_assets_list
from .library_configurator import LibraryConfiguratorWidget
from .product import ProductWidget
from .tag import TagWidget


def _get_system_presets(self, context):
    items = []
    presets = [
        preset for preset in scattersystempresetstore.get_all() if not preset.is_terrain
    ]
    for index, preset in enumerate(presets):
        items.append((preset.id, preset.name, "", "", index))

    return items


def enumerate_environments(self, context: bpy.types.Context):
    enum = [
        (
            "SELECT_TEMPLATE",
            "Select Environment",
            "",
            previews.get(icons.get_icon_path("select_template")).icon_id,
            0,
        )
    ]
    for idx, environment in enumerate(self.environments):
        enum.append(
            (
                environment.asset_id,
                environment.name,
                environment.description,
                environment.previews.get_gallery_preview(),
                idx + 1,
            )
        )

    return enum


environment_items = []


def get_environment_items(self, context):
    return environment_items


class LibraryWidget(BaseWidget):
    name: StringProperty(name="Name", default="Library")
    products: CollectionProperty(name="Products", type=ProductWidget)
    assets: CollectionProperty(name="Assets", type=AssetWidget)
    environments: CollectionProperty(name="Environments", type=EnvironmentWidget)
    environment_enums: EnumProperty(name="Environments", items=get_environment_items)
    tags: CollectionProperty(name="Tags", type=TagWidget)
    configurators: CollectionProperty(
        name="Configurators", type=LibraryConfiguratorWidget
    )
    page: IntProperty(name="Page", default=1)
    presets: EnumProperty(name="Presets", items=_get_system_presets)
    free_assets: CollectionProperty(name="Free Assets", type=FreeAssetWidget)

    loading_free_assets: BoolProperty(default=False)
    free_assets_count: IntProperty(default=0)
    syncing_assets: BoolProperty(default=False)
    syncing_assets_progress: FloatProperty(
        name="Progress", min=0, max=100, subtype="PERCENTAGE"
    )

    def get_environment_by_id(self, asset_id: str):
        for env in self.environments:
            if env.asset_id == asset_id:
                return env

    def get_environment_by_name(self, name: str):
        for env in self.environments:
            if env.name == name:
                return env

    def update_search(self, context: Context):
        queries = self.search.lower().split()

        def filter_asset(asset: AssetWidget) -> bool:
            name = asset.name.lower()

            if queries and any(query not in name for query in queries):
                return False

            tags = [tag.name for tag in self.tags if tag.select]

            if tags and all(tag not in asset.tags for tag in tags):
                return False

            return True

        result = list(
            filter(
                filter_asset,
                self.assets
                if self.browse_type == "ASSETS"
                else self.environments
                if self.browse_type == "ENVIRONMENTS"
                else self.free_assets,
            )
        )
        self.result = repr(result)

        if result:
            number_of_pages = self.number_of_pages()
            if self.page > number_of_pages:
                self.page = number_of_pages

    search: StringProperty(
        name="Search", update=update_search, options={"TEXTEDIT_UPDATE"}
    )
    result: StringProperty(name="Result")

    def update_browse_type(self, context):
        self.search = self.search

    browse_type: EnumProperty(
        name="Browse",
        items=[
            ("ASSETS", "Assets", ""),
            ("ENVIRONMENTS", "Environments", ""),
            # ("DOWNLOAD", "Download Assets", ""),
        ],
        update=update_browse_type,
    )

    def filtered_assets(self) -> list[AssetWidget]:
        if self.result:
            return eval(self.result)
        else:
            return (
                self.assets.values()
                if self.browse_type == "ASSETS"
                else self.environments.values()
                if self.browse_type == "ENVIRONMENTS"
                else self.free_assets.values()
            )

    def visible_assets(self) -> list[AssetWidget]:
        assets = self.filtered_assets()
        offset = self.asset_offset()
        items_per_page = self.items_per_page()
        return assets[offset : offset + items_per_page]

    def selected_assets(self, context: bpy.context = None) -> list[AssetWidget]:
        if context is None:
            context = bpy.context
        space_data = context.space_data
        if asset_utils.SpaceAssetInfo.is_asset_browser(space_data):
            selection = []
            try:
                if context.selected_asset_files:
                    selection = context.selected_asset_files
            except AttributeError:
                if context.selected_assets:
                    selection = context.selected_assets
            selected = [
                self.assets[product.name.removeprefix(". ")]
                if get_asset_type_from_asset_browser(product) == "3D_PLANT"
                else self.get_environment_by_name(product.name.removeprefix(". "))
                if get_asset_type_from_asset_browser(product) == "ENVIRONMENT"
                else None
                for product in selection
                if get_asset_type_from_asset_browser(product)
                in ["3D_PLANT", "ENVIRONMENT"]
            ]

            return [selected[0]] if selected else []

        if self.browse_type == "ASSETS":
            return [asset for asset in self.assets if asset.select]
        elif self.browse_type == "ENVIRONMENTS":
            return [
                environment for environment in self.environments if environment.select
            ]
        return [free_asset for free_asset in self.free_assets if free_asset.select]

    def get_asset(self, asset_id: str) -> Union[AssetWidget, None]:
        for asset in self.assets:
            if asset.asset_id.lower() == asset_id.lower():
                return asset

    def configurator_for_asset(self, asset: AssetWidget) -> LibraryConfiguratorWidget:
        if asset.configurator.name in self.configurators:
            return self.configurators[asset.configurator.name]
        else:
            return self.configurators["standard"]

    def assets_for_configurator(
        self, configurator: LibraryConfiguratorWidget
    ) -> list[AssetWidget]:
        def check(asset):
            return self.configurator_for_asset(asset) == configurator

        return [asset for asset in self.selected_assets() if check(asset)]

    def asset_offset(self) -> int:
        return (self.page - 1) * self.items_per_page()

    def focus_asset(self, offset: int):
        self.page = offset // self.items_per_page() + 1

    def columns_and_rows(self) -> tuple:
        prefs = get_preferences()
        columns = prefs.asset_browser_columns
        rows = prefs.asset_browser_rows

        if self.selected_assets():
            return (columns - 2, rows)
        else:
            return (columns, rows)

    def items_per_page(self) -> int:
        columns, rows = self.columns_and_rows()
        return columns * rows

    def number_of_pages(self) -> int:
        assets = self.filtered_assets()
        items_per_page = self.items_per_page()
        return math.ceil(len(assets) / items_per_page)

    def refresh_configurators(self):
        for configurator in self.configurators:
            configurator.refresh_properties()

    def check_configurators(self) -> bool:
        return not self.configurators or all(
            configurator.check_properties() for configurator in self.configurators
        )

    def load(self, data: dict, get_free_asset=False):
        self.property_unset("page")

        self["search"] = ""
        self["result"] = ""

        self.products.clear()
        for product_data in data.get("products", []):
            product = self.products.add()
            product.load(product_data)

        self.assets.clear()
        for asset_data in data.get("assets", []):
            asset = self.assets.add()
            asset.load(asset_data)

        self.tags.clear()
        for name in data.get("tags", []):
            tag = self.tags.add()
            tag.name = name

        self.environments.clear()
        for environment_data in data.get("environments", []):
            environment = self.environments.add()
            environment.load(environment_data)

        self.configurators.clear()
        for name, module in modules.items():
            configurator = self.configurators.add()
            configurator.load({"name": name, "properties": module.properties})

        global environment_items
        environment_items = enumerate_environments(self, bpy.context)

        # Free Asset Check, prevent losing state from clearing items in progress. Finished Installed Assets Widgets already remove themselves.
        for free_asset in self.free_assets:
            if free_asset.downloading or free_asset.installing:
                return

        if get_free_asset and get_allow_networking():
            self.free_assets.clear()
            utils.clear_free_assets_entries()
            self.loading_free_assets = True

            def get_assets(data, create_entry):
                if data is None:
                    return

                self.free_assets_count = len(data.get("assets", []))
                for asset_data in data.get("assets", []):
                    try:
                        free_asset = self.free_assets.add()
                        free_asset.load(asset_data, create_entry)

                    except Exception as e:
                        error(e, "Couldn't load", debug=True)

            def on_done():
                self.loading_free_assets = False
                bpy.context.view_layer.update()

                def refresh() -> None:
                    bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

                bpy.app.timers.register(refresh)
                # try:
                #     os.system("cls")
                # except:
                #     ...

            get_free_assets_list(get_assets, on_done)
        else:
            self.free_assets.clear()
            user_library = get_asset_browser_dir()
            asset_list_path = user_library.joinpath("free_assets.json")
            free_assets_list = {}
            if asset_list_path.exists():
                f = open(asset_list_path, "r")
                free_assets_list = json.load(f)
                f.close()
            for asset_data in free_assets_list.get("assets", []):
                try:
                    free_asset = self.free_assets.add()
                    free_asset.load(asset_data, False)
                except Exception:
                    ...

    def draw(self, layout: UILayout, split_factor: float):
        selected = self.selected_assets()

        self.draw_search(layout)

        if selected:
            split = layout.split(factor=split_factor)
            browser = split.column(align=True)
            sidebar = split.column(align=True)
        else:
            browser = layout.column(align=True)

        self.draw_browser(browser)
        self.draw_navigation(browser)
        if selected:
            self.draw_sidebar(sidebar)

    def draw_item_selector(self, layout: UILayout, effect_name: str, input_name: str):
        # selected = self.selected_assets()

        self.draw_search(layout)

        browser = layout.column(align=True)

        self.draw_mini_browser(browser, effect_name, input_name)
        self.draw_navigation(browser)

    def draw_search(self, layout: UILayout):
        row = layout.row()
        row.scale_y = 1.4

        split = row.split(factor=0.5)
        split_row = split.row()

        browse = split_row.row(align=True)
        browse.prop(self, "browse_type", expand=True)

        split_row = split.row()

        search = split_row.row(align=True)
        search.prop(self, "search", text="", icon="VIEWZOOM")

        filters = split_row.row(align=True)
        filters.operator(FilterPopup.bl_idname, text="", icon="FILTER")

        clear = filters.row(align=True)
        clear.enabled = any(tag.select for tag in self.tags)
        clear.operator(ClearTagsOperator.bl_idname, text="", icon="X")

        install = split_row.row(align=True)
        install.operator(RefreshLibraryOperator.bl_idname, text="", icon="FILE_REFRESH")
        install.operator(InstallAssetsOperator.bl_idname, text="", icon="IMPORT")

        layout.separator()

    def draw_browser(self, layout: UILayout):
        columns, _ = self.columns_and_rows()
        items_per_page = self.items_per_page()
        visible = self.visible_assets()

        grid = layout.grid_flow(
            row_major=True, columns=columns, even_columns=True, even_rows=True
        )

        for asset in visible:
            col = grid.column(align=True)
            asset.draw_gallery(col)
            col.separator()

        for _ in range(items_per_page - len(visible)):
            col = grid.column(align=True)
            AssetWidget.draw_blank(col)
            col.separator()

    def draw_mini_browser(self, layout: UILayout, effect_name: str, input_name: str):
        columns, _ = self.columns_and_rows()
        items_per_page = self.items_per_page()
        visible = self.visible_assets()

        grid = layout.grid_flow(
            row_major=True, columns=columns, even_columns=True, even_rows=True
        )

        for asset in visible:
            col = grid.column(align=True)
            asset.draw_item(col, effect_name, input_name)
            col.separator()

        for _ in range(items_per_page - len(visible)):
            col = grid.column(align=True)
            AssetWidget.draw_blank(col)
            col.separator()

    def draw_navigation(self, layout: UILayout):
        number_of_pages = self.number_of_pages()

        if number_of_pages <= 5:
            first_page, last_page = 1, number_of_pages
        elif self.page <= 3:
            first_page, last_page = 1, 5
        elif self.page >= (number_of_pages - 3):
            first_page, last_page = (number_of_pages - 4), number_of_pages
        else:
            first_page, last_page = (self.page - 2), (self.page + 2)

        row = layout.row()
        row.alignment = "CENTER"

        sub = row.row()
        sub.enabled = self.page > 1
        sub.operator(
            ScrollPageLeftOperator.bl_idname, text="", icon="TRIA_LEFT", emboss=False
        )

        for index in range(first_page, (last_page + 1)):
            row.operator(
                SelectPageOperator.bl_idname,
                text=str(index),
                emboss=(index == self.page),
                depress=True,
            ).index = index

        sub = row.row()
        sub.enabled = self.page < self.number_of_pages()
        sub.operator(
            ScrollPageRightOperator.bl_idname, text="", icon="TRIA_RIGHT", emboss=False
        )

    def draw_products(self, context: bpy.types.Context, layout: UILayout):
        selected_asset_file = context.active_file

        asset_type = get_asset_type_from_asset_browser(selected_asset_file)
        if asset_type == "3D_PLANT":
            self.refresh_configurators()
            asset = self.assets.get(selected_asset_file.name)
            if asset is None:
                return
            asset.draw_details(layout)

            for configurator in self.configurators:
                configurator_assets = []
                for asset in [asset]:
                    if self.configurator_for_asset(asset) == configurator:
                        configurator_assets.append(asset)

                if configurator_assets:
                    col: bpy.types.UILayout = configurator.draw_properties(
                        layout
                    ).column()
                    col.scale_x = col.scale_y = 1.4
                    col.use_property_split = True
                    col.use_property_decorate = False
                    col.prop(self, "presets", text="Presets")

                    layout.separator()

            gscatter = bpy.context.scene.gscatter
            if not gscatter.scatter_surface:
                split = layout.box().split(factor=0.4)
                split.scale_y = 1.4

                row = split.row()
                row.alignment = "RIGHT"

                row.label(text="Emitter")
                split.prop(gscatter, "scatter_surface", text="")

            row = layout.row(align=True)
            row.enabled = self.check_configurators()
            row.scale_y = 1.8
            op = row.operator(
                ScatterSelectedOperator.bl_idname,
                text="Scatter Selected",
                icon_value=icons.get("graswald"),
            )
            op.individual = False
            op.preset = self.presets
            op.asset_type = "GRASWALD"

            row.operator(
                AddToSceneOperator.bl_idname, text="Add to Scene", icon="SCENE_DATA"
            )
        elif asset_type == "ENVIRONMENT":
            environment = self.get_environment_by_name(
                selected_asset_file.name.removeprefix(". ")
            )
            if environment:
                environment.draw_details(layout)

                layout.separator()
                col = layout.column()
                col.scale_y = 1.3

                col.operator(AddEnvironmentOperator.bl_idname)
        elif asset_type == "FREE_ASSET":
            free_asset = self.free_assets.get(selected_asset_file.name)
            if free_asset:
                free_asset.draw_details(layout)
        else:
            asset_type = context.active_file.rna_type
            col = layout.column(align=True)
            col.box().template_icon(
                icon_value=context.active_file.preview_icon_id,
                scale=utils.icon_scale_from_res(200),
            )
            col.box().operator(
                DummyOperator.bl_idname,
                text=context.active_file.name.removeprefix(". ").removeprefix("_ "),
                emboss=False,
            )

            if context.active_file.asset_data.description:
                box = col.box()
                text_col = box.column(align=True)
                text_col.scale_y = 0.8
                for text in wrap_text(
                    context.active_file.asset_data.description,
                    bpy.context.region.width,
                ):
                    text_col.label(text=text)
            col.separator()
            col = col.column()
            col.prop(self, "presets", text="Presets")
            col.separator()
            col = col.column()
            col.scale_y = 1.6

            op = col.operator(
                ScatterSelectedOperator.bl_idname,
                text="Scatter Selected",
                icon_value=icons.get("graswald"),
            )
            op.individual = False
            op.preset = self.presets
            op.asset_type = asset_type

    def draw_assets_sidebar(self, layout: UILayout):
        selected_assets = self.selected_assets()
        if not selected_assets or self.browse_type != "ASSETS":
            return
        if len(selected_assets) == 1:
            asset = selected_assets[0]
            asset.draw_details(layout)

            layout.separator()

            configurator = self.configurator_for_asset(asset)
            col: bpy.types.UILayout = configurator.draw_properties(layout).column()
            col.scale_x = col.scale_y = 1.4
            col.use_property_split = True
            col.use_property_decorate = False
            col.prop(self, "presets", text="Presets")

            layout.separator()

        else:
            for configurator in self.configurators:
                assets = self.assets_for_configurator(configurator)
                debug(f"Drawing multiple assets for {len(assets)} assets")
                if assets:
                    box = layout.box()

                    for asset in assets:
                        asset.draw_list_item(box)

                    col: bpy.types.UILayout = configurator.draw_properties(
                        layout
                    ).column()
                    col.scale_x = col.scale_y = 1.4
                    col.use_property_split = True
                    col.use_property_decorate = False
                    col.prop(self, "presets", text="Presets")

                    layout.separator()

        gscatter = bpy.context.scene.gscatter

        if not gscatter.scatter_surface:
            split = layout.box().split(factor=0.4)
            split.scale_y = 1.4

            row = split.row()
            row.alignment = "RIGHT"

            row.label(text="Emitter")
            split.prop(gscatter, "scatter_surface", text="")

        row = layout.row(align=True)
        # row.enabled = self.check_configurators()
        row.scale_y = 1.8
        op = row.operator(
            ScatterSelectedOperator.bl_idname,
            text="Scatter Selected",
            icon_value=icons.get("graswald"),
        )
        op.individual = False
        op.preset = self.presets

        row.operator(
            AddToSceneOperator.bl_idname, text="Add to Scene", icon="SCENE_DATA"
        )

    def draw_environment_sidebar(self, layout: UILayout):
        selected_environments = self.selected_assets()
        if not selected_environments or self.browse_type != "ENVIRONMENTS":
            return

        for environment in selected_environments:
            environment.draw_details(layout)

        layout.separator()
        col = layout.column()
        col.scale_y = 1.3

        col.operator(AddEnvironmentOperator.bl_idname)

    def draw_free_asset_sidebar(self, layout: UILayout):
        selected = self.selected_assets()
        if not selected or self.browse_type != "DOWNLOAD":
            return

        for asset in selected:
            asset.draw_details(layout)

    def draw_sidebar(self, layout: UILayout):
        self.draw_assets_sidebar(layout)
        self.draw_environment_sidebar(layout)
        self.draw_free_asset_sidebar(layout)

    def draw_tags(self, layout: UILayout):
        if self.tags:
            layout.label(text="Filters")

            col = layout.column(align=True)
            col.scale_y = 1.2

            for tag in self.tags:
                tag.draw(col)

        else:
            layout.label(text="No Filters Found")


classes = (LibraryWidget,)


@bpy.app.handlers.persistent
def load_library_handler(self, context):
    asset_list_path = get_asset_browser_dir().joinpath("free_assets.json")
    if not bpy.app.background:
        utils.load_library(not asset_list_path.exists())


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    WindowManagerProps.library = PointerProperty(name="Library", type=LibraryWidget)
    bpy.app.handlers.load_post.append(load_library_handler)


def unregister():
    del WindowManagerProps.library

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
