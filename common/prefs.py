from pathlib import Path

import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty, StringProperty
from bpy.types import AddonPreferences, Context, UILayout

from .. import icons
from ..asset_manager.callbacks import create_library
from ..scatter.store import scattersystempresetstore
from ..utils.getters import get_package, get_preferences
from ..utils.logger import update_log_level
from .props import ProxySettingsProps


def set_loglevel(self, dephs):
    prefs = get_preferences()
    loglevel = 0 if prefs.enable_developer_mode else 25
    update_log_level(loglevel)


def _get_system_presets(self, context):
    items = []
    presets = [
        preset for preset in scattersystempresetstore.get_all() if not preset.is_terrain
    ]
    for index, preset in enumerate(presets):
        items.append((preset.id, preset.name, "", "", index))

    return items


class GScatterPreferences(AddonPreferences):
    bl_idname = get_package()

    # NOTE: Renaming this means users have to set it again.
    uid: StringProperty(name="UID", default="")
    show_tutorial_popup: BoolProperty(default=True)
    ignore_compatibility_warning: BoolProperty(
        name="Compatibility Warning", default=False
    )

    t3dn_library: StringProperty(
        name="Library Directory",
        subtype="DIR_PATH",
        default=str(Path.home().joinpath("Documents", "GScatter")),
        update=create_library,
    )

    asset_browser_columns: IntProperty(
        name="Asset Browser Columns", default=6, min=4, max=8
    )
    asset_browser_rows: IntProperty(name="Asset Browser Rows", default=3, min=2, max=4)
    gscatter_collection_name: StringProperty(name="Collection Name", default="GScatter")

    enable_experimental_features: BoolProperty(
        name="Enable Experimental Features", default=False, update=create_library
    )
    enable_developer_mode: BoolProperty(
        name="Enable Developer Mode", default=False, update=set_loglevel
    )

    use_proxy_on_new_systems: BoolProperty(
        name="Enable Proxy On New Systems",
        default=False,
        description="Set wether or not a new scatter system should have the proxy mode automatically enabled",
    )
    proxy_method_items = ProxySettingsProps.proxy_method_items
    proxy_method: EnumProperty(
        items=proxy_method_items,
        name="Default Proxy Method",
        description="Select the default proxy method, \ndoesn't change the current selected proxy method",
        default="Convex Hull",
    )
    default_scatter_preset: EnumProperty(
        items=_get_system_presets,
        name="Default System Preset",
        description="Select the system preset \nwith which new scatter systems will be created",
    )
    asset_import_mode: EnumProperty(
        name="Asset Import Mode",
        items=[
            ("APPEND", "Append", "Append selected assets>"),
            ("LINK", "Link", "Link selected assets>"),
        ],
        default="LINK",
    )
    asset_browser_window_size: EnumProperty(
        name="Asset Browser Window Size",
        items=[
            ("small", "Small", "Small window size"),
            ("medium", "Medium", "Medium size window"),
            ("big", "Big", "Big window"),
        ],
        default="medium",
    )
    asset_browser_docked: BoolProperty(
        name="Dock Asset Browser",
        default=False,
    )
    asset_browser_dock_side: EnumProperty(
        name="Select Docked Asset Browser Side",
        items=[
            ("up", "Dock Top", "Dock to the top of the current view"),
            ("down", "Dock Bottom", "Dock to the bottom of the current view"),
            ("left", "Dock Left", "Dock to the left of the current view"),
            ("right", "Dock Right", "Dock to the right of the current view"),
        ],
        default="left",
    )

    def draw_property(
        self, parent, data, property: str, text=None, factor=0.6, align=True
    ):
        if text:
            row = parent.split(factor=factor, align=align)
            row.prop(data, property, text="")
            row.label(text=text)
        else:
            row = parent.row()
            row.prop(data, property)

    def draw_category_box(
        self, parent, title, icon: str | int | None = "NONE", icon_value: int = 0
    ):
        col = parent.column(align=True)
        box = col.box()
        box.separator(factor=1)
        row = box.row()
        row.separator(factor=3)
        row.label(text=title, icon=icon, icon_value=icon_value)
        row.separator(factor=5)

        box = col.box()
        row = box.split(factor=0.05, align=True)
        row.label(text="")
        col = row.column()
        return col

    def draw(self, context: Context):
        layout: UILayout = self.layout
        column = layout.column()

        right_col = column  # split.column()

        # GSCATTER OPTIONS
        col = self.draw_category_box(
            right_col, title="Gscatter Basic Options", icon_value=icons.get("graswald")
        )
        self.draw_property(col, self, "gscatter_collection_name", "Collection Name")
        self.draw_property(
            col, self, "default_scatter_preset", "Default Scatter Preset"
        )
        self.draw_property(col, self, "proxy_method", "Default Proxy Method")
        # row.label(text="Default Proxy Method")
        row = col.row()
        rr = row.row()
        rr.alignment = "LEFT"
        rr.prop(self, "use_proxy_on_new_systems")

        # ASSETBROWSER
        col = self.draw_category_box(
            right_col,
            title="Asset Browser",
            icon="ASSET_MANAGER",
            icon_value=icons.get("graswald"),
        )
        self.draw_property(col, self, "t3dn_library", "Library Directory")
        self.draw_property(col, self, "asset_import_mode", "Asset Import Mode")
        col.separator()

        self.draw_property(col, self, "asset_browser_columns", "Asset Browser Columns")
        self.draw_property(col, self, "asset_browser_rows", "Asset Browser Rows")
        col.separator()

        self.draw_property(
            col, self, "asset_browser_window_size", "Asset Browser Window Size"
        )
        self.draw_property(
            col, self, "asset_browser_dock_side", "Asset Browser Dock Side"
        )
        row = col.split(factor=0.4, align=True)
        rr = row.row()
        rr.alignment = "LEFT"
        rr.prop(self, "asset_browser_docked")

        # Left main Column
        left_col = column  # split.column()

        # FLAGS
        col = self.draw_category_box(
            left_col, title="Advanced Settings", icon="TOOL_SETTINGS"
        )
        col.prop(self, "enable_experimental_features")
        col.prop(self, "enable_developer_mode")

        column.separator()

        row = column.row()
        row.alignment = "CENTER"
        row.label(text="A Graswald product", icon_value=icons.get("graswald"))


classes = (GScatterPreferences,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
