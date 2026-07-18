import bpy

from ..utils.logger import debug
from ..utils.getters import (
    get_node_tree,
    get_scatter_props,
    get_scene_props,
    get_preferences,
)
from . import default

from bpy.app.handlers import persistent


class ScatterItemProps(bpy.types.PropertyGroup):
    """Group of properties representing an item in the Scatter Items list."""

    def _update_proxy_color(self, context):
        self.obj.color = self.color
        mat = bpy.data.materials.get("proxy_" + self.obj.name, None)
        if mat:
            mat.diffuse_color = self.color

    def _update_viewport_proxy(self, context):
        gscatter_props: SceneProps = get_scene_props(bpy.context)
        proxy_settings = gscatter_props.proxy_settings
        proxy_method = proxy_settings.proxy_method
        display_type = "TEXTURED"
        mute = not self.viewport_proxy

        if proxy_method == "Bounds" and self.viewport_proxy:
            display_type = "BOUNDS"
            mute = True
        _toggle_proxy_effect(self.obj, display_type, mute)

    def get_ntree_version(self):
        return tuple(self.ntree_version)

    def _update_name(self, context):
        node_group = bpy.data.node_groups.get(self.obj.name)
        if node_group:
            node_group.name = self.name
        self.obj.name = self.name

    def _update_camera_culling(self, context):
        node = _get_effect(self.obj, "CAMERA_CULLING")
        node.mute = not self.camera_culling

    ntree_version: bpy.props.IntVectorProperty(
        name="Nodetree Version", default=(1, 0, 0)
    )
    obj: bpy.props.PointerProperty(type=bpy.types.Object)
    name: bpy.props.StringProperty(default="")
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=4,
        min=0,
        max=1,
        soft_max=1,
        soft_min=0,
        update=_update_proxy_color,
    )
    proxy_mat: bpy.props.PointerProperty(type=bpy.types.Material, name="Proxy material")
    viewport_proxy: bpy.props.BoolProperty(
        name="Viewport Proxy",
        description="Toggle Viewport Proxy",
        default=False,
        update=_update_viewport_proxy,
    )
    environment_selection: bpy.props.BoolProperty(name="Select", default=True)
    camera_culling: bpy.props.BoolProperty(
        name="", default=True, update=_update_camera_culling
    )

    @property
    def is_terrain(self) -> bool:
        if self.obj:
            return self.obj.gscatter.is_terrain
        return False

    @is_terrain.setter
    def is_terrain(self, value):
        if self.obj:
            self.obj.gscatter.is_terrain = value


class ObjectProps(bpy.types.PropertyGroup):
    def update_obj_scatter_items(self):
        scatter_items = self.scatter_items
        # Check if given obj is used in current ScatterSystems
        if not scatter_items:
            return

        for index, item in enumerate(scatter_items):
            obj_in_system = False
            modifier = item.obj.modifiers.get("GScatterGeometryNodes")
            try:
                if modifier is None:
                    return
                if modifier.node_group is None:
                    return
                main_tree = modifier.node_group
                if modifier.node_group.nodes["Join Geometry"] is None:
                    return
                for object_info in main_tree.nodes["Join Geometry"].inputs[0].links:
                    object_info_node = object_info.from_node
                    input = object_info_node.inputs[0].default_value
                    debug(f"Input {input.name}")
                    if input == self.id_data:
                        obj_in_system = True

                if not obj_in_system:
                    scatter_items.remove(index)  # Clear Effect from list

                if item.is_terrain and index == len(scatter_items) - 1:
                    scene_props = get_scene_props()
                    scene_props.active_category = "GEOMETRY"

            except Exception:
                continue
                #
                """input = main_tree.nodes.new("GeometryNodeObjectInfo")
                input.inputs[0].default_value = obj
                input.location = (
                    0,
                    len(main_tree.nodes["Join Geometry"].inputs[0].links) * -200,
                )
                input.name = obj.name
                input.transform_space = "RELATIVE"
                main_tree.links.new(
                    output=input.outputs[3],
                    input=main_tree.nodes["Join Geometry"].inputs[0],
                )"""

    def _update_scatter_index(self, context: bpy.types.Context):
        if self.scatter_index in range(len(self.scatter_items)):
            si: ScatterItemProps = self.scatter_items[self.scatter_index]
            si_obj: bpy.types.Object = si.obj

            for ob in context.selected_objects:
                ob: bpy.types.Object
                ob.select_set(False)

            try:
                si_obj.select_set(True)
                context.view_layer.objects.active = si_obj
            except Exception:
                ...

            if si.is_terrain:
                scene_props = get_scene_props(context)
                scene_props.active_category = "GEOMETRY"

    scatter_items: bpy.props.CollectionProperty(
        type=ScatterItemProps
    )  # All Systems on this Emitter
    scatter_index: bpy.props.IntProperty(
        name="Select Scatter System \n\u2022 Double click to rename.",
        update=_update_scatter_index,
    )  # Selected Scatter System
    is_gscatter_system: bpy.props.BoolProperty(default=False)
    is_terrain: bpy.props.BoolProperty(default=False)
    ss: bpy.props.PointerProperty(name="Scatter Surface", type=bpy.types.Object)


def _get_effect(obj, id):
    node_tree = get_node_tree(obj)
    node: bpy.types.GeometryNodeGroup = node_tree.nodes[id]
    return node


def _get_effects_by_effect_id(id):
    effects = []
    for obj in bpy.data.objects:
        node_tree = get_node_tree(obj)
        if node_tree is None:
            continue
        for category in default.EFFECT_CATEGORIES:
            node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
            all_effects = node.node_tree.gscatter.effects
            for effect in all_effects:
                if effect.get_effect_id() == id:
                    effects.append(effect)
    return effects


def _get_effects_per_item(obj, id):
    effects = []
    node_tree = get_node_tree(obj)
    if node_tree is None:
        return
    for category in default.EFFECT_CATEGORIES:
        node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
        all_effects = node.node_tree.gscatter.effects
        for effect in all_effects:
            if effect.get_effect_id() == id:
                effects.append(effect)
    return effects


def _get_effects(context, id):
    scatter_props = get_scatter_props(context)
    if not scatter_props:
        return []
    scatter_items = scatter_props.scatter_items
    effects_nodes = [_get_effect(item.obj, id) for item in scatter_items]
    return effects_nodes


def set_active_camera(self, context):
    scene_props = bpy.context.scene.gscatter
    if scene_props.camera_culling.camera != bpy.context.scene.camera:
        scene_props.camera_culling.camera = bpy.context.scene.camera


def _toggle_proxy_effect(obj, display_type, mute):
    node_tree = get_node_tree(obj)
    if node_tree is None:
        return
    node: bpy.types.GeometryNodeGroup = node_tree.nodes["VIEWPORT_PROXY"]
    node.mute = mute

    # Set display_type to "Bounds"
    obj.display_type = display_type


class CameraCullingProps(bpy.types.PropertyGroup):
    """Group of properties representing a camera culling."""

    def _update_camera_culling(self, context):
        scatter_props = get_scatter_props(context)
        if not scatter_props:
            return []
        scatter_items = scatter_props.scatter_items
        effects_nodes = [
            _get_effect(item.obj, self.ID)
            for item in scatter_items
            if item.camera_culling
        ]
        for node in effects_nodes:
            node.mute = not self.use

    def _update_camera(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[1].default_value = self.camera

    def _update_focal_length(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[2].default_value = self.focal_length

    def _update_sensor_size(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[3].default_value = self.sensor_size

    def _update_render_width(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[4].default_value = self.render_width

    def _update_render_height(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[5].default_value = self.render_height

    def _update_buffer(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[6].default_value = self.buffer

    def _update_backface_culling(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[7].default_value = self.backface_culling

    def _update_backface_threshold(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[8].default_value = self.backface_threshold

    def _update_distance_culling(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[9].default_value = self.distance_culling

    def _update_distance_threshold(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs[10].default_value = self.distance_threshold

    def _update_use_active_camera(self, context):
        if self.use_active_camera:
            set_active_camera(self, context)
            bpy.app.handlers.depsgraph_update_post.append(set_active_camera)
            bpy.app.handlers.frame_change_post.append(set_active_camera)
        else:
            bpy.app.handlers.depsgraph_update_post.remove(set_active_camera)
            bpy.app.handlers.frame_change_post.remove(set_active_camera)

    ID = "CAMERA_CULLING"
    use: bpy.props.BoolProperty(
        default=False, name="Use camera culling", update=_update_camera_culling
    )
    use_active_camera: bpy.props.BoolProperty(
        name="Use Active Camera", default=False, update=_update_use_active_camera
    )
    camera: bpy.props.PointerProperty(
        type=bpy.types.Object, name="Camera", update=_update_camera
    )
    focal_length: bpy.props.FloatProperty(
        default=50, name="Focal Length", update=_update_focal_length
    )
    sensor_size: bpy.props.FloatProperty(
        default=36, name="Sensor Size", update=_update_sensor_size
    )
    render_width: bpy.props.FloatProperty(
        default=16, name="Render Width", update=_update_render_width
    )
    render_height: bpy.props.FloatProperty(
        default=9, name="Render Height", update=_update_render_height
    )
    buffer: bpy.props.FloatProperty(default=0, name="Buffer", update=_update_buffer)
    backface_culling: bpy.props.BoolProperty(
        default=True, name="Backface Culling", update=_update_backface_culling
    )
    backface_threshold: bpy.props.FloatProperty(
        default=0.2,
        min=0.0,
        max=1.0,
        name="Backface Threshold",
        update=_update_backface_threshold,
    )
    distance_culling: bpy.props.BoolProperty(
        default=True, name="Distance Culling", update=_update_distance_culling
    )
    distance_threshold: bpy.props.FloatProperty(
        default=100, min=0, name="Distance Threshold", update=_update_distance_threshold
    )


class ProxySettingsProps(bpy.types.PropertyGroup):
    """Group of properties representing theproxy settings"""

    def _update_proxy_method(self, context):
        method = False
        mute = False
        display_type = "TEXTURED"
        if self.proxy_method == self.BOUNDS:
            display_type = "BOUNDS"
            mute = True
        if self.proxy_method == self.POINT_CLOUD:
            method = True
        for node in _get_effects(context, self.ID):
            node.inputs["Point Cloud"].default_value = method

        # Bounds Proxy Mode
        scatter_props = get_scatter_props(context)
        if not scatter_props:
            return
        scatter_items = scatter_props.scatter_items
        for scatter_item in scatter_items:
            if scatter_item.viewport_proxy:
                _toggle_proxy_effect(scatter_item.obj, display_type, mute)

    def _update_pc_density(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs["Density"].default_value = self.pc_density

    def _update_pc_size(self, context):
        for node in _get_effects(context, self.ID):
            node.inputs["Radius"].default_value = self.pc_size

    ID = "VIEWPORT_PROXY"
    POINT_CLOUD = "Point Cloud"
    CONVEX_HULL = "Convex Hull"
    BOUNDS = "Bounds"
    proxy_method_items = (
        (POINT_CLOUD, POINT_CLOUD, POINT_CLOUD),
        (CONVEX_HULL, CONVEX_HULL, CONVEX_HULL),
        (BOUNDS, BOUNDS, BOUNDS),
    )
    proxy_method: bpy.props.EnumProperty(
        items=proxy_method_items, name="Proxy Method", update=_update_proxy_method
    )
    pc_density: bpy.props.FloatProperty(
        default=10, name="Point Cloud Density", update=_update_pc_density
    )
    pc_size: bpy.props.FloatProperty(
        default=0.15, name="Point Size", update=_update_pc_size
    )


class SceneProps(bpy.types.PropertyGroup):
    def update_viewport_percentage(self, context: bpy.context):
        face_dist_effects = _get_effects_by_effect_id("system.distribute_on_faces")
        for effect in face_dist_effects:
            effect.effect_node.inputs[
                4
            ].default_value = self.viewport_display_percentage

    def scatter_surface_poll(self, object):
        return object.type not in (
            "LIGHT",
            "LIGHT_PROBE",
            "CAMERA",
            "SPEAKER",
            "VOLUME",
        )

    def scatter_surface_update(self, context: bpy.context):
        ss = self.scatter_surface
        if ss:
            ss.gscatter.update_obj_scatter_items()

    scatter_surface: bpy.props.PointerProperty(
        name="Scatter Surface",
        description="Select the mesh to scatter on",
        type=bpy.types.Object,
        poll=scatter_surface_poll,
        update=scatter_surface_update,
    )

    hide_original: bpy.props.BoolProperty(
        name="Auto hide original object", default=True
    )
    camera_culling: bpy.props.PointerProperty(
        name="Camera culling", type=CameraCullingProps
    )
    use_active_object_as_scatter_surface: bpy.props.BoolProperty(
        name="Active",
        default=False,
        description="Always switch the active object to be the emitter",
    )
    proxy_settings: bpy.props.PointerProperty(
        name="Proxy Settings", type=ProxySettingsProps
    )
    viewport_display_percentage: bpy.props.IntProperty(
        name="Viewport Display %",
        default=100,
        min=0,
        max=100,
        subtype="PERCENTAGE",
        update=update_viewport_percentage,
    )


class WindowManagerProps(bpy.types.PropertyGroup):
    compatibility_warning: bpy.props.BoolProperty(default=False)
    ignore_compatibility_warning: bpy.props.BoolProperty(default=False)
    new_preset: bpy.props.StringProperty(name="New Preset", default="New Preset")
    system: bpy.props.StringProperty()


classes = (
    ScatterItemProps,
    ObjectProps,
    CameraCullingProps,
    ProxySettingsProps,
    SceneProps,
    WindowManagerProps,
)


@persistent
def set_proxy_method(
    scene,
):  # persistent so it runs every time a scene is loaded/created
    pref = get_preferences().proxy_method
    get_scene_props().proxy_settings.proxy_method = pref


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.gscatter = bpy.props.PointerProperty(type=ObjectProps)
    bpy.types.Scene.gscatter = bpy.props.PointerProperty(type=SceneProps)
    bpy.types.WindowManager.gscatter = bpy.props.PointerProperty(
        type=WindowManagerProps
    )

    bpy.app.handlers.load_post.append(set_proxy_method)


def unregister():
    del bpy.types.WindowManager.gscatter
    del bpy.types.Scene.gscatter
    del bpy.types.Object.gscatter
    bpy.app.handlers.load_post.remove(set_proxy_method)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
