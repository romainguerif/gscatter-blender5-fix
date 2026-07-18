from itertools import zip_longest
from math import ceil

from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import Context, PropertyGroup, UILayout
from bpy.utils import register_class, unregister_class
from .. import icons
from ..common.props import WindowManagerProps
from .ops import SelectIconOperator


class IconViewerWidget(PropertyGroup):
    columns: IntProperty(name="Columns", default=40, min=1)

    @property
    def rows(self) -> int:
        return ceil(len(self.results) / self.columns)

    @property
    def width(self) -> int:
        return self.columns * 20

    @property
    def height(self) -> int:
        return self.rows * 20

    def get_selected(self) -> str:
        return self.get("selected", "")

    def set_selected(self, value: str):
        pass

    selected: StringProperty(name="Selected Icon", get=get_selected, set=set_selected)
    history: CollectionProperty(type=PropertyGroup)
    results: CollectionProperty(type=PropertyGroup)

    @property
    def all_icons(self) -> list[str]:
        blender_icons = (
            UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()
        )
        custom_icons = [icon for icon in icons.get_all() if icons.is_custom(icon)]
        return blender_icons + custom_icons

    def update(self, context: Context):
        icons = []
        search = self.search.upper()

        for icon in self.all_icons:
            if icon == "NONE":
                continue

            if search not in icon:
                continue

            if not self.show_brush_icons:
                if "BRUSH_" in icon:
                    if icon != "BRUSH_DATA":
                        continue

            if not self.show_event_icons:
                if "EVENT_" in icon:
                    continue
                if "MOUSE_" in icon:
                    continue

            if not self.show_color_icons:
                if "COLORSET_" in icon:
                    continue
                if "COLLECTION_COLOR_" in icon:
                    continue
                if "SEQUENCE_COLOR_" in icon:
                    continue

            icons.append(icon)

        if self.sort_by_name:
            icons.sort()
        if self.sort_reverse:
            icons.reverse()

        self.results.clear()
        for icon in icons:
            self.results.add().name = icon

    def select(self, icon: str):
        if icon in self.history:
            self.history.remove(self.history.find(icon))

        self.history.add().name = icon
        self["selected"] = icon

    search: StringProperty(
        name="Search", default="", update=update, options={"TEXTEDIT_UPDATE"}
    )
    show_brush_icons: BoolProperty(name="Show Brush Icons", default=True, update=update)
    show_event_icons: BoolProperty(name="Show Event Icons", default=True, update=update)
    show_color_icons: BoolProperty(name="Show Color Icons", default=True, update=update)
    sort_by_name: BoolProperty(name="Sort By Name", default=False, update=update)
    sort_reverse: BoolProperty(name="Sort Reverse", default=False, update=update)

    def draw(self, layout: UILayout):
        col = layout.column(align=True)
        row = col.row()
        row.scale_x, row.scale_y = 1.4, 1.4

        row.operator("gscatter.reload_icons", text="", icon="FILE_REFRESH")

        sub = row.row(align=True)
        sub.prop(self, "show_brush_icons", text="", icon="BRUSH_DATA")
        sub.prop(self, "show_color_icons", text="", icon="COLOR")
        sub.prop(self, "show_event_icons", text="", icon="HAND")

        sub = row.row(align=True)
        sub.prop(self, "sort_by_name", text="", icon="SORTALPHA")
        sub.prop(
            self,
            "sort_reverse",
            text="",
            icon="SORT_DESC" if self.sort_reverse else "SORT_ASC",
        )

        row.prop(self, "search", text="", icon="VIEWZOOM")
        if self.selected:
            if icons.is_custom(self.selected):
                row.prop(self, "selected", text="", icon_value=icons.get(self.selected))
            else:
                row.prop(self, "selected", text="", icon=self.selected)

        col.separator()

        if self.history:
            self.draw_icons(col.box(), history=True)
        if self.results:
            self.draw_icons(col.box())
        else:
            col.box().label(text="No icons found")

    def draw_icons(self, layout: UILayout, history: bool = False):
        col = layout.column(align=True)

        all_icons = reversed(self.history.keys()) if history else self.results.keys()
        chunks = list(zip_longest(*[iter(all_icons)] * self.columns))

        for chunk in chunks:
            row = col.row(align=True)

            for icon in chunk:
                if icon:
                    sel = icon == self.selected
                    if icons.is_custom(icon):
                        op = row.operator(
                            SelectIconOperator.bl_idname,
                            text="",
                            icon_value=icons.get(icon),
                            emboss=sel,
                            depress=sel,
                        )
                    else:
                        op = row.operator(
                            SelectIconOperator.bl_idname,
                            text="",
                            icon=icon,
                            emboss=sel,
                            depress=sel,
                        )
                    op.icon = icon
                else:
                    row.label(text="", icon="BLANK1")

            if history:
                break


classes = (IconViewerWidget,)


def register():
    for cls in classes:
        register_class(cls)

    WindowManagerProps.icon_viewer = PointerProperty(type=IconViewerWidget)


def unregister():
    del WindowManagerProps.icon_viewer

    for cls in reversed(classes):
        unregister_class(cls)
