import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

import bpy
from bpy.types import Object, Operator
from ..asset_manager.utils import create_asset_browser_entry, load_library
from ..slow_task_manager.scopped_slow_task import StartSlowTask
from ..utils.getters import (
    get_materials_in_system,
    get_preferences,
    get_scatter_props,
    get_scatter_system_effects,
    get_scene_props,
    get_wm_props,
)
from . import default, utils
from .utils import add_environment, get_effect

if TYPE_CHECKING:
    from ..asset_manager.props.library import LibraryWidget


class CreateEnvironmentOperator(Operator):
    """Create a environment from current scatter surface"""

    bl_idname = "gscatter.create_environment"
    bl_label = "Create Environment"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        scene_props = get_scene_props(context)
        environment_creator = scene_props.environment_creator
        if (
            environment_creator.name.strip() == ""
            or environment_creator.preview.strip() == ""
            or environment_creator.terrain_material is None
        ):
            return False
        return True

    def invoke(self, context, event):
        if not bpy.data.is_saved or bpy.data.is_dirty:
            self.report({"ERROR"}, message="Please save your blend file first.")
            return {"CANCELLED"}
        return self.execute(context)

    def execute(self, context):
        scene_props = get_scene_props(context)
        scatter_surface = scene_props.scatter_surface
        environment_creator = scene_props.environment_creator
        scatter_props = get_scatter_props(context)
        library: "LibraryWidget" = context.window_manager.gscatter.library
        systems = []
        gscatter_assets = []

        dependency_objs = list()
        dependency_cols = list()
        dependency_images = list()
        dependency_mats = list()

        # add it to users library
        prefs = get_preferences(context)
        user_lib = prefs.t3dn_library
        environments_dir = Path(user_lib, "Environments")
        environment_path = environments_dir.joinpath(environment_creator.name)

        # Get systems
        for scatter_item in scatter_props.scatter_items:
            if scatter_item.environment_selection:
                obj: Object = scatter_item.obj
                (
                    distribution,
                    scale,
                    rotation,
                    geometry,
                    assets,
                    dependencies,
                ) = get_scatter_system_effects(obj)

                for ob in dependencies["objects"]:
                    dependency_objs.append(ob.name)
                for col in dependencies["collections"]:
                    dependency_cols.append(col.name)
                for img in dependencies["images"]:
                    dependency_images.append(img.name)
                for mat in dependencies["materials"]:
                    dependency_mats.append(mat.name)

                gscatter_assets += assets
                systems.append(
                    {
                        "name": scatter_item.obj.name,
                        "color": list(scatter_item.color),
                        "distribution": distribution,
                        "scale": scale,
                        "rotation": rotation,
                        "geometry": geometry,
                    }
                )

        environment_data = {
            "asset_type": "environment",
            "asset_id": str(uuid4()),
            "name": environment_creator.name,
            "description": environment_creator.description,
            "author": environment_creator.author,
            "schema_version": default.SCHEMA_VERSION,
            "gscatter_systems": systems,
            "blends": [],
            "preview": f"images/gallery.{environment_creator.preview.split('.')[-1]}",
            "gscatter_assets": gscatter_assets,
        }

        asset_paths = []
        for asset_id in gscatter_assets:
            asset = library.get_asset(asset_id)
            if asset is None:
                self.report({"ERROR"}, message=f"{asset_id} is missing. Cancelled")
                return {"CANCELLED"}
            asset_path = Path(asset.blends[0].name).parent.parent
            asset_paths.append((asset_id, asset_path))

        environments_dir.mkdir(exist_ok=True, parents=True)
        environment_path.mkdir(exist_ok=True, parents=True)

        environment_asset_dir = environment_path.joinpath("Assets")
        environment_asset_dir.mkdir(exist_ok=True, parents=True)

        with StartSlowTask("Copying Assets", len(asset_paths)) as copy_task:
            for idx in range(len(asset_paths)):
                asset_id = asset_paths[idx][0]
                asset_path = asset_paths[idx][1]

                copy_task.set_progress(idx)
                copy_task.set_progress_text(f"Copying assets {idx}/{len(asset_paths)}")
                copy_task.refresh()

                asset_src_path = asset_path
                asset_dst_path = environment_asset_dir.joinpath(asset_id)
                asset_dst_path.mkdir(exist_ok=True, parents=True)
                shutil.copytree(asset_src_path, asset_dst_path, dirs_exist_ok=True)

        with StartSlowTask(
            f"Creating data.blend file for {environment_creator.name}", 1
        ) as creating_data:
            creating_data.set_progress(0)
            creating_data.set_progress_text(
                f"Creating data.blend file for {environment_creator.name}"
            )
            creating_data.refresh()

            environment_props = []
            for prop in scatter_surface.gscatter.environment_props.props:
                effect = get_effect(context, scatter_surface, prop.effect_instance_id)
                if effect is None:
                    continue
                for input in effect.effect_node.inputs:
                    if input.identifier == prop.input:
                        environment_props.append(
                            {
                                "label": prop.label,
                                "effect_instance_id": prop.effect_instance_id,
                                "input": prop.input,
                                "input_idx": prop.input_idx,
                                "input_type": input.type,
                                "order_idx": prop.order_idx,
                            }
                        )
            environment_data["environment_props"] = environment_props

            terrain_data = {"material": environment_creator.terrain_material.name}
            material_names = []
            if scatter_surface.gscatter.is_terrain:
                (
                    distribution,
                    scale,
                    rotation,
                    geometry,
                    _,
                    terrain_dependencies,
                ) = get_scatter_system_effects(scatter_surface)
                terrain_system = {
                    "name": scatter_surface.name,
                    "is_terrain": scatter_surface.gscatter.is_terrain,
                    "distribution": distribution,
                    "scale": scale,
                    "rotation": rotation,
                    "geometry": geometry,
                }
                terrain_data.update(
                    {
                        "name": scatter_surface.name,
                        "system": terrain_system,
                    }
                )
                materials = get_materials_in_system(scatter_surface)
                materials.add(environment_creator.terrain_material)
                material_names += [mat.name for mat in materials]

            # Create the data.blend file
            blender_exec = Path(bpy.app.binary_path)
            script_path = (
                Path(__file__).parent.joinpath("data_blend_creator.py").resolve()
            )
            script_path = str(script_path)
            src_blend_path = bpy.data.filepath
            data_dir = environment_path.joinpath("data")
            data_dir.mkdir(exist_ok=True, parents=True)
            dest_blend_path = data_dir.joinpath("data.blend")

            blender_cmd = [
                blender_exec,
                "-b",
                "-P",
                script_path,
                "--",
                src_blend_path,
                dest_blend_path.as_posix(),
                str(material_names),
                str(dependency_objs),
                str(dependency_cols),
                str(dependency_images),
                str(dependency_mats),
            ]
            process = subprocess.Popen(blender_cmd, shell=True)

            while not dest_blend_path.exists():
                time.sleep(0.5)

            process.terminate()
            environment_data["terrain"] = terrain_data
            environment_data["blends"] = ["data/data.blend"]
            product_json = json.dumps(environment_data, indent=4)

            with open(environment_path.joinpath("product.json"), "w") as f:
                f.write(product_json)
            images_dir = environment_path.joinpath("images")
            images_dir.mkdir(exist_ok=True, parents=True)

            shutil.copyfile(
                environment_creator.preview,
                images_dir.joinpath(
                    f"gallery.{environment_creator.preview.split('.')[-1]}"
                ),
            )

            if prefs.enable_experimental_features:
                create_asset_browser_entry(
                    context,
                    environment_data["name"],
                    environment_data,
                    "ENVIRONMENT",
                    environment_path,
                )
                # debug(result)
                load_library()

            creating_data.set_progress(1)
            creating_data.set_progress_text(
                f"Creatind data.blend file for {environment_creator.name}"
            )
            creating_data.refresh()
            time.sleep(1)

        self.report({"INFO"}, message="Environment created successfully.")
        return {"FINISHED"}


class PreviewOperator(bpy.types.Operator):
    bl_idname = "gscatter.set_environment_preview"
    bl_label = "Set Preview Image"
    bl_description = "Opens file selector, after executes"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.png;*.jpeg;*.jpg;",
        options={"HIDDEN"},
    )

    def execute(self, context):
        scene_props = get_scene_props()
        scene_props.environment_creator.preview = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class AddEnvironmentOperator(Operator):
    bl_idname = "gscatter.add_environment"
    bl_description = "Add the selected Environment"
    bl_label = "Add Environment"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        wm_props = get_wm_props(context)
        starter_props = wm_props.scatter_starter
        if (
            starter_props.terrain_type == "CUSTOM"
            and starter_props.custom_terrain is None
        ):
            return False
        return True

    def execute(self, context):
        get_scene_props(context)
        library: "LibraryWidget" = context.window_manager.gscatter.library

        selected = library.selected_assets()

        with StartSlowTask("Adding Environment", len(selected)) as main_task:
            for i in range(len(selected)):
                environment = selected[i]
                effect_trees = dict()

                main_task.set_progress(i)
                main_task.set_progress_text(environment["name"])
                main_task.refresh()

                add_environment(context, environment, effect_trees)

        self.report({"INFO"}, message="Environment Added successfully.")
        return {"FINISHED"}


class ScrollEnvironmentsOperator(bpy.types.Operator):
    bl_idname = "gscatter.scroll_environments"
    bl_label = "Scroll Environment"
    bl_description = "Scroll through all installed environments"
    bl_options = {"REGISTER", "INTERNAL"}

    environment: bpy.props.StringProperty(name="environment")
    direction: bpy.props.IntProperty(name="Direction")

    def execute(self, context: bpy.types.Context) -> set:
        library = context.window_manager.gscatter.library
        for idx, environment in enumerate(library.environments):
            if (
                environment.asset_id == self.environment
                or self.environment == "SELECT_TEMPLATE"
            ):
                if self.environment == "SELECT_TEMPLATE":
                    idx = 0 if self.direction == -1 else -1

                # environment = eval(self.environment)
                # curr_index = library.environments.index(environment)

                idx += self.direction
                idx %= len(library.environments)
                library.environment_enums = library.environments[idx].asset_id
                break

        return {"FINISHED"}


class EffectItems(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    instance_id: bpy.props.StringProperty()


class PropertyInfo(Operator):
    bl_idname = "gscatter.show_env_prtoperty_info"
    bl_label = "Show Environment Property Info"

    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, operator):
        return operator.tooltip

    def execute(self, context: bpy.types.Context) -> set:
        return {"CANCELLED"}


class AddNewEnvironmentPropertyOperator(Operator):
    bl_idname = "gscatter.add_environment_property"
    bl_description = "Add new environment property"
    bl_label = "Add Environment Property"
    bl_options = {"UNDO"}

    def get_inputs(self, context):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        env_props = ss.gscatter.environment_props.props
        effect = utils.get_effect(context, ss, self.effect_instance_id)
        inputs = [("SELECT", "Select Input", "")]
        if effect:
            effect_node = effect.effect_node
            for inp in effect_node.inputs:
                if (
                    not inp.is_linked
                    and hasattr(inp, "default_value")
                    and inp.enabled
                    and inp.hide_value is False
                    and not any(prop.input == inp.identifier for prop in env_props)
                ):
                    inputs.append((inp.identifier, inp.name, inp.description))
        inputs.sort(key=lambda x: x[1])
        return inputs

    def update_effect(self, context):
        for effect in self.effects:
            if effect.name == self.effect:
                self.effect_instance_id = effect.instance_id

        self.inputs = "SELECT"
        self.input_label = ""

    def update_input(self, context):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        effect = utils.get_effect(context, ss, self.effect_instance_id)
        if effect:
            for idx, input in enumerate(effect.effect_node.inputs):
                if input.identifier == self.inputs:
                    self.input_label = input.name
                    self.input_idx = idx
                    break

    effect: bpy.props.StringProperty(name="Effect", update=update_effect)
    input_idx: bpy.props.IntProperty()
    inputs: bpy.props.EnumProperty(name="Inputs", items=get_inputs, update=update_input)
    input_label: bpy.props.StringProperty()
    effect_instance_id: bpy.props.StringProperty()

    effects: bpy.props.CollectionProperty(name="Effects", type=EffectItems)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        row = layout.row()
        row.prop_search(
            self,
            "effect",
            self,
            "effects",
        )
        col = layout.column()
        col.enabled = True if self.effect.strip() != "" else False
        col.prop(self, "inputs")
        col.prop(self, "input_label", text="Property label")

    def invoke(self, context, event):
        self.effect = ""
        self.effects.clear()
        self.effect_instance_id = ""
        self.inputs = "SELECT"
        self.input_idx = 0
        self.input_label = ""

        effects = []
        scatter_props = get_scatter_props(context)
        for scatter_item in scatter_props.scatter_items:
            obj: Object = scatter_item.obj
            distribution, scale, rotation, geometry, _, _ = get_scatter_system_effects(
                obj
            )
            for effect in distribution + scale + rotation + geometry:
                effects.append((effect["name"], effect["effect_instance_id"]))
        effects.sort()
        for effect in effects:
            new_effect_entry = self.effects.add()
            new_effect_entry.name = effect[0]
            new_effect_entry.instance_id = effect[1]
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.input_label == "" or self.inputs == "SELECT":
            self.report(
                {"ERROR_INVALID_INPUT"}, message="Need to provide a valid input"
            )
            return {"CANCELLED"}
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        env_props = ss.gscatter.environment_props.props
        new_prop_entry = env_props.add()
        new_prop_entry.label = self.input_label
        new_prop_entry.effect_instance_id = self.effect_instance_id
        new_prop_entry.input = self.inputs
        new_prop_entry.input_idx = self.input_idx
        new_prop_entry.order_idx = len(ss.gscatter.environment_props.props) - 1
        self.report({"INFO"}, message="Property Added.")
        return {"FINISHED"}


class RenameProperty(Operator):
    bl_idname = "gscatter.rename_environment_property"
    bl_description = "Rename environment property"
    bl_label = "Rename Property"
    bl_options = {"UNDO"}

    prop_idx: bpy.props.IntProperty()
    new_name: bpy.props.StringProperty(name="Name")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_name")

    def invoke(self, context, event):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        env_props = ss.gscatter.environment_props.props

        prop = env_props[self.prop_idx]
        self.new_name = prop.label
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        env_props = ss.gscatter.environment_props.props

        prop = env_props[self.prop_idx]
        prop.label = self.new_name
        return {"FINISHED"}


class ReorderPropertyOperator(Operator):
    bl_idname = "gscatter.reorder_environment_property"
    bl_description = "Reorder environment property"
    bl_label = "Reorder Property"
    bl_options = {"UNDO"}

    prop_idx: bpy.props.IntProperty()
    direction: bpy.props.EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")])

    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, operator):
        return operator.tooltip

    def execute(self, context):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        env_props = ss.gscatter.environment_props.props

        prop = env_props[self.prop_idx]

        if self.direction == "UP":
            try:
                before = next(p for p in env_props if p.order_idx == prop.order_idx - 1)
                before.order_idx += 1
            except Exception:
                pass
            prop.order_idx -= 1
            if prop.order_idx < 0:
                prop.order_idx = 0

        else:
            try:
                after = next(p for p in env_props if p.order_idx == prop.order_idx + 1)
                after.order_idx -= 1
            except Exception:
                pass
            prop.order_idx += 1
            if prop.order_idx > len(env_props) - 1:
                prop.order_idx = len(env_props) - 1
        return {"FINISHED"}


class RemovePropertyOperator(Operator):
    bl_idname = "gscatter.remove_environment_property"
    bl_description = "Remove environment property"
    bl_label = "Remove Property"
    bl_options = {"UNDO"}

    prop_idx: bpy.props.IntProperty()

    def execute(self, context):
        scene_props = get_scene_props(context)
        ss = scene_props.scatter_surface
        env_props = ss.gscatter.environment_props.props
        env_props.remove(self.prop_idx)

        props = list(env_props)
        props.sort(key=lambda x: x.order_idx)

        for idx, prop in enumerate(props):
            prop.order_idx = idx
        return {"FINISHED"}


classes = (
    EffectItems,
    PreviewOperator,
    CreateEnvironmentOperator,
    AddEnvironmentOperator,
    AddNewEnvironmentPropertyOperator,
    ScrollEnvironmentsOperator,
    RenameProperty,
    ReorderPropertyOperator,
    RemovePropertyOperator,
    PropertyInfo,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
