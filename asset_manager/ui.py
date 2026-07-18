from typing import TYPE_CHECKING

import bpy
from bpy.types import Context, Panel
from bpy_extras import asset_utils


from . import default
from .ops.install import (
    AssetBrowserInstallAssetsOperator,
    DeleteCatalogEntryOperator,
    SyncInstalledAssetsOperator,
)
from .asset_browser import get_asset_browser_windows

if TYPE_CHECKING:
    from .props.library import LibraryWidget


class GScatterAssetBrowserPanel(asset_utils.AssetMetaDataPanel, Panel):
    bl_idname = "GSCATTER_PT_AssetBrowserPanel"
    bl_label = "Gscatter"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context: Context):
        return (
            get_asset_browser_windows()
            and context.window in get_asset_browser_windows()
        )

    def draw(self, context: Context):
        layout = self.layout
        active_file = context.active_file
        library: "LibraryWidget" = context.window_manager.gscatter.library
        params = context.area.spaces.active.params

        # if library.loading_free_assets:
        #     col =layout.box().column(align=True)
        #     col.label(text=f"Please wait while we are loading",
        #               icon="QUESTION")
        #     col.label(text=f"{library.free_assets_count} free assets.",
        #               icon="BLANK1")

        if active_file:
            library.draw_products(context, layout)

        if (
            library.loading_free_assets
            or params.catalog_id == default.ASSETS_CATALOG_ID
            or params.catalog_id == default.ENVIRONMENTS_CATALOG_ID
            or params.catalog_id == default.FREE_ASSET_CATALOG_ID
        ):
            return

        layout.separator()
        layout.operator(
            DeleteCatalogEntryOperator.bl_idname,
            text="Delete Selected Asset Catalog",
            icon="TRASH",
        ).catalog_id = params.catalog_id


class GScatterAssetBrowserPropPanel(asset_utils.AssetBrowserPanel, Panel):
    bl_label = " "
    bl_region_type = "TOOLS"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context: Context):
        return (
            get_asset_browser_windows()
            and context.window in get_asset_browser_windows()
        )

    def draw(self, context: Context):
        layout = self.layout
        col = layout.column()
        col.scale_y = 1000000000000000
        col.label(text=" YOOO ")


def disable_metadata_panel(cls, context: Context):
    if (
        not get_asset_browser_windows()
        or context.window not in get_asset_browser_windows()
    ) or (
        not hasattr(context.area.spaces.active.params, "asset_library_reference")
        and not hasattr(context.area.spaces.active.params, "asset_library_ref")
    ):
        return cls.poll_orig(context)
    return False


def draw_gscatter_browser_header(self, context: Context):
    library: "LibraryWidget" = context.window_manager.gscatter.library
    if (
        not get_asset_browser_windows()
        or context.window not in get_asset_browser_windows()
    ):
        self.draw_orig(context)
        return

    if not hasattr(
        context.area.spaces.active.params, "asset_library_ref"
    ) and not hasattr(context.area.spaces.active.params, "asset_library_reference"):
        self.draw_orig(context)
        return

    space_data = context.space_data
    params = space_data.params
    layout: bpy.types.UILayout = self.layout

    layout.box().label(text="GScatter Asset Browser", icon="ASSET_MANAGER")
    layout.separator_spacer()
    sub = layout.row()
    sub.ui_units_x = 8
    sub.prop(params, "filter_search", text="", icon="VIEWZOOM")
    layout.separator_spacer()

    row = layout.row()
    # op = row.operator(RefreshLibraryOperator.bl_idname, text='Refresh', icon='FILE_REFRESH')
    # op.load_free_assets = False
    row.operator(
        AssetBrowserInstallAssetsOperator.bl_idname, text="Install Asset", icon="IMPORT"
    )
    if library.syncing_assets:
        rr = row.row()
        rr.enabled = False
        rr.prop(
            library,
            "syncing_assets_progress",
            slider=True,
            text="Syncing Old Assets...",
        )
    else:
        row.operator(
            SyncInstalledAssetsOperator.bl_idname,
            text="Sync Old Assets",
            icon="TRACKING",
        )

    # Uses prop_with_popover() as popover() only adds the triangle icon in headers.
    layout.prop_with_popover(
        params,
        "display_type",
        panel="ASSETBROWSER_PT_display",
        text="",
        icon_only=True,
    )


classes = (GScatterAssetBrowserPanel,)


def update_poll(type):
    type.poll_orig = type.poll
    type.poll = classmethod(disable_metadata_panel)


def revert_poll(type):
    type.poll = type.poll_orig


def register():
    update_poll(bpy.types.ASSETBROWSER_PT_metadata)
    update_poll(bpy.types.ASSETBROWSER_MT_editor_menus)
    update_poll(bpy.types.ASSETBROWSER_PT_metadata_preview)
    update_poll(bpy.types.ASSETBROWSER_PT_metadata_tags)

    bpy.types.FILEBROWSER_HT_header.draw_orig = bpy.types.FILEBROWSER_HT_header.draw
    bpy.types.FILEBROWSER_HT_header.draw = draw_gscatter_browser_header

    asset_utils.AssetBrowserPanel.poll_orig = asset_utils.AssetBrowserPanel.poll
    asset_utils.AssetBrowserPanel.poll = classmethod(disable_metadata_panel)

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    revert_poll(bpy.types.ASSETBROWSER_PT_metadata)
    revert_poll(bpy.types.ASSETBROWSER_MT_editor_menus)
    revert_poll(bpy.types.ASSETBROWSER_PT_metadata_preview)
    revert_poll(bpy.types.ASSETBROWSER_PT_metadata_tags)

    bpy.types.FILEBROWSER_HT_header.draw = bpy.types.FILEBROWSER_HT_header.draw_orig
    asset_utils.AssetBrowserPanel.poll = asset_utils.AssetBrowserPanel.poll_orig

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
