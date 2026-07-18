import bpy
from ..utils import main_collection, getters


class RealizeSystemOperator(bpy.types.Operator):
    bl_idname = "gscatter.realize_scatter_system"
    bl_label = "Realize System"
    bl_description = "Realize System's Instances as real objects with shared data"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        active_object = context.active_object
        if (
            active_object is not None
            and active_object.type == "MESH"
            and context.mode == "OBJECT"
            and active_object.select_get()
            and active_object.gscatter.is_gscatter_system
        ):
            return True
        return False

    def execute(self, context: bpy.types.Context):
        col_name = f"{bpy.context.active_object.name} Instances"
        instances_col = bpy.data.collections.new(col_name)
        system_col = main_collection(None, "Systems")
        system_col.children.link(instances_col)

        override = context.copy()
        with context.temp_override(**override):
            bpy.ops.object.duplicates_make_real()

        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            instances_col.objects.link(obj)
        self.report({"INFO"}, "Realized All Instances")
        return {"FINISHED"}


class ApplySystemOperator(bpy.types.Operator):
    bl_idname = "gscatter.apply_scatter_system"
    bl_label = "Apply Scatter System"
    bl_description = "Apply Scatter System, which merges all plants to a new single mesh \n\u2022 Warning! \nCan result in very high polycounts and will slow down your system"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        if (
            active_object is not None
            and active_object.type == "MESH"
            and context.mode == "OBJECT"
            and active_object.select_get()
            and active_object.gscatter.is_gscatter_system
        ):
            return True
        return False

    def execute(self, context):
        active_object = context.active_object
        merged_obj = active_object.copy()

        system_col = main_collection(None, "Systems")
        system_col.objects.link(merged_obj)

        active_object.select_set(False)
        context.view_layer.objects.active = merged_obj
        merged_obj.select_set(True)
        merged_obj.name = f"{active_object.name} Merged"
        merged_obj.gscatter.is_gscatter_system = False

        nodes_modifier = getters.get_nodes_modifier(merged_obj)
        system_tree = getters.get_system_tree(merged_obj)
        new_system_tree = system_tree.copy()
        nodes_modifier.node_group = new_system_tree

        real_inst_node = new_system_tree.nodes.new("GeometryNodeRealizeInstances")
        real_inst_node.location = (600, -100)

        group_output = new_system_tree.nodes.get("Group Output")
        gscatter_node_group = new_system_tree.nodes.get("GScatter")

        new_system_tree.links.new(
            real_inst_node.inputs[0], gscatter_node_group.outputs[0]
        )
        new_system_tree.links.new(group_output.inputs[0], real_inst_node.outputs[0])

        override = context.copy()
        override["active_object"] = merged_obj
        with context.temp_override(**override):
            bpy.ops.object.convert()

        bpy.data.node_groups.remove(new_system_tree)
        return {"CANCELLED"}


classes = (
    RealizeSystemOperator,
    ApplySystemOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
