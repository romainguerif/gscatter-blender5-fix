from typing import TYPE_CHECKING

import bpy

from ...scatter.functions import scatter_collection, scatter_objects
from ...scatter.utils import get_selected_asset
from ...utils.getters import get_wm_props
from ..configurators import configure

if TYPE_CHECKING:
    from ..props.library import LibraryWidget


class AddToSceneOperator(bpy.types.Operator):
    bl_idname = "gscatter.add_to_scene"
    bl_label = "Add to Scene"
    bl_description = "Add the selected assets to the scene"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set:
        wm_props = get_wm_props(context)
        library: "LibraryWidget" = wm_props.library

        for asset in library.selected_assets():
            collection = configure(asset)
            if collection.name not in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.link(collection)

        bpy.ops.object.select_all(action="DESELECT")

        message = "Successfully added to Scene!"
        self.report({"INFO"}, message)
        bpy.ops.gscatter.popup_message("INVOKE_DEFAULT", message=message, width=200)

        return {"FINISHED"}


class ScatterSelectedOperator(bpy.types.Operator):
    bl_idname = "gscatter.scatter_selected"
    bl_label = "Scatter Selected"
    bl_description = "Scatter the selected assets on the chosen surface.\n\u2022 Ctrl and click to scatter individually"
    bl_options = {"INTERNAL", "UNDO"}

    individual: bpy.props.BoolProperty(
        name="Scatter Individually",
        description="Create a scatter system for each selected object",
        default=False,
    )
    preset: bpy.props.StringProperty(name="Preset", default="system.default")
    asset_type: bpy.props.EnumProperty(
        items=[
            ("GRASWALD", "Graswald", ""),
            ("COLLECTION", "Collection", ""),
            ("OBJECT", "Object", ""),
        ]
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        wm_props = get_wm_props(context)
        library: "LibraryWidget" = wm_props.library
        return context.scene.gscatter.scatter_surface and (
            library.selected_assets(context) or context.active_file
        )

    def invoke(self, context, event):
        if event.ctrl:
            self.individual = True
        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set:
        wm_props = get_wm_props(context)
        library: "LibraryWidget" = wm_props.library
        if self.asset_type == "GRASWALD":
            for asset in library.selected_assets(context):
                try:
                    collection = configure(asset)
                    collection.gscatter.is_gscatter_asset = True
                    collection.gscatter.asset_id = asset.asset_id
                    if self.individual:
                        scatter_objects(
                            [ob for ob in collection.objects], True, self.preset, True
                        )
                    else:
                        scatter_collection(collection, self.preset)
                except:
                    raise

                else:
                    message = "Individual" if self.individual else "Together"
            # bpy.context.space_data.shading.color_type = 'OBJECT'
        elif self.asset_type in ["COLLECTION", "OBJECT"]:
            cols = get_selected_asset(context.area)
            for col in cols:
                if self.individual:
                    scatter_objects(
                        [obj for obj in col.objects], self.individual, self.preset
                    )
                else:
                    scatter_collection(col, self.preset)
                message = "Individual" if self.individual else "Together"

        message = "Successfully scattered!"
        self.report({"INFO"}, message)
        bpy.ops.gscatter.popup_message("INVOKE_DEFAULT", message=message, width=200)

        return {"FINISHED"}


classes = (
    AddToSceneOperator,
    ScatterSelectedOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
