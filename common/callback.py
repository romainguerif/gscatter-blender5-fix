import bpy
from bpy.app.handlers import persistent

from ..utils import logger, startup
from ..utils.getters import get_preferences, get_scene_props


@persistent
def check_camera_culling_use_active_camera(self, context: bpy.types.Context):
    scene_props = get_scene_props(context)

    if scene_props.camera_culling.use_active_camera:
        scene_props.camera_culling._update_use_active_camera(context)


@persistent
def set_active_object_as_scatter_surface(self, dep: bpy.types.Depsgraph):
    scene_props = get_scene_props(bpy.context)
    if scene_props.use_active_object_as_scatter_surface:
        active = bpy.context.active_object
        if active == scene_props.scatter_surface:
            return

        if active and active.type not in [
            "CAMERA",
            "LIGHT",
            "CURVES",
            "EMPTY",
            "ARMATURE",
            "LIGHT_PROBES",
        ]:
            scene_props.scatter_surface = active


def default_log_level():
    prefs = get_preferences()
    logger.logger.setLevel(0 if prefs.enable_developer_mode else 25)  # Default level


def tutorial_popup_handler(cl=None, clx=None):
    prefs = get_preferences()
    if prefs.show_tutorial_popup:
        bpy.ops.gscatter.show_tutorial_popup("INVOKE_DEFAULT")


def register():
    startup.add_callback(tutorial_popup_handler)
    startup.add_callback(default_log_level)
    # bpy.app.handlers.load_post.append(tutorial_popup_handler)
    bpy.app.handlers.load_post.append(check_camera_culling_use_active_camera)
    bpy.app.handlers.depsgraph_update_post.append(set_active_object_as_scatter_surface)


def unregister():
    bpy.app.handlers.load_post.remove(check_camera_culling_use_active_camera)
    bpy.app.handlers.depsgraph_update_post.remove(set_active_object_as_scatter_surface)
