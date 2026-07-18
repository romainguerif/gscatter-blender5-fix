from typing import List

import bpy
from bpy.app.handlers import persistent

from ..common.props import ScatterItemProps
from ..utils.getters import get_scatter_props, get_scene_props
from . import default


@persistent
def active_object_change_handler(self, depsgraph: bpy.types.Depsgraph):
    scatter_props = get_scatter_props(depsgraph)
    if scatter_props is not None:
        scatter_items: List[ScatterItemProps] = scatter_props.scatter_items

        for index, item in enumerate(scatter_items):
            obj: bpy.types.Object = item.obj

            if obj is depsgraph.view_layer.objects.active:
                if scatter_props.scatter_index != index:
                    scatter_props["scatter_index"] = index
                    break


@persistent
def object_deleted_handler(self, context: bpy.types.Context):
    scatter_props = get_scatter_props(context)
    if scatter_props is not None:
        scatter_items: List[ScatterItemProps] = scatter_props.scatter_items
        should_update_index = False

        for index, item in enumerate(scatter_items):
            obj: bpy.types.Object = item.obj

            if (obj is None) or (obj.users == 1):
                scatter_items.remove(index)
                should_update_index = True

        if should_update_index:
            scatter_props["scatter_index"] = len(scatter_items) - 1

    reset_scatter_surface()


@persistent
def check_scatter_system_versions(self, context: bpy.types.Context):
    scatter_props = get_scatter_props(context)
    if scatter_props is not None:
        scatter_items: List[ScatterItemProps] = scatter_props.scatter_items

        for item in scatter_items:
            if item.get_ntree_version() != default.NODETREE_VERSION:
                bpy.ops.gscatter.update_scatter_system_tree(
                    "INVOKE_DEFAULT", mode="ALL"
                )
                break


def reset_scatter_surface():
    scene_props = get_scene_props(bpy.context)
    obj: bpy.types.Object = scene_props.scatter_surface
    if (
        scene_props.scatter_surface
        and scene_props.scatter_surface.name not in bpy.context.view_layer.objects
    ):
        scene_props.scatter_surface = None
        if obj.users == 0:
            bpy.data.objects.remove(obj)


def register():
    bpy.app.handlers.depsgraph_update_post.append(active_object_change_handler)
    bpy.app.handlers.depsgraph_update_post.append(object_deleted_handler)
    bpy.app.handlers.load_post.append(check_scatter_system_versions)


def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(object_deleted_handler)
    bpy.app.handlers.depsgraph_update_post.remove(active_object_change_handler)
