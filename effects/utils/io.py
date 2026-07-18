import json
from typing import Any, List, Tuple, Union

import bpy
from . import inputs
from ..models import EffectMetaData

EXCLUDE_PROPS = {"bl_rna"}

FLOAT_MIN = -1e20
FLOAT_MAX = 1e20

# TODO: Import these once we drop 2.93 support.
NON_PRIMITIVE_SOCKETS = {
    "NodeSocketGeometry",
    "NodeSocketMaterial",
    "NodeSocketTexture",
}


def clean(value: Any) -> Union[str, list, Any, None]:
    """Cleans arbitrary datatypes for conversion to string."""
    if isinstance(value, str):
        return value
    if hasattr(value, "__len__"):
        return list(value)
    if hasattr(value, "__add__"):
        return value
    return None


class EffectReader:
    def read_meta_data(self, data: dict):
        meta_data = EffectMetaData(
            name=data["name"],
            description=data["description"],
            author=data["author"],
            icon=data["icon"],
            schema_version=data["schema_version"],
            blender_version=data["blender_version"],
            categories=data["category"],
            subcategory=data["subcategory"],
        )
        return meta_data

    def read_node(self, group, data: dict):
        node = group.nodes.new(data["type"])
        node.name = data["name"]
        # node.label = data["label"]

        if isinstance(node, bpy.types.GeometryNodeGroup):
            node.node_tree = self.read_node_group(data["node_group"])

        else:
            props = data.get("props", {})
            for key, value in props.items():
                if key == "display_in_effect":
                    node.gscatter.display_in_effect = value
                elif key == "display_order":
                    node.gscatter.display_order = value
                else:
                    setattr(node, key, value)

            if "color_ramp" in data:
                i = 0
                for pos, color in data["color_ramp"][:2]:
                    c = node.color_ramp.elements[i]
                    c.position = pos
                    c.color = color
                    i += 1
                for pos, color in data["color_ramp"][2:]:
                    c = node.color_ramp.elements.new(pos)
                    c.color = color
            elif "curve_float" in data:
                for i, p in enumerate(data["curve_float"][1:-1]):
                    i += 1
                    node.mapping.curves[0].points.new(p[0][0], p[0][1])
                    node.mapping.curves[0].points[i].handle_type = p[1]
                point_first = data["curve_float"][0]
                point_last = data["curve_float"][-1]
                node.mapping.curves[0].points[0].handle_type = point_first[1]
                node.mapping.curves[0].points[0].location = point_first[0]
                node.mapping.curves[0].points[-1].handle_type = point_last[1]
                node.mapping.curves[0].points[-1].location = point_last[0]

    def read_input(self, group, data: dict):
        try:
            input = group.input.new_socket(data["type"], data["name"])
        except Exception:
            input = group.interface.ui_items.new_socket(data["type"], data["name"])

        if data.get("min") is not None:
            input.min_value = data["min"]
        if data.get("max") is not None:
            input.max_value = data["max"]
        if data.get("default") is not None:
            input.default_value = data["default"]

    def read_node_group(self, data: dict) -> bpy.types.GeometryNodeTree:
        name: str = data["name"]
        nodes: List[dict] = data["nodes"]
        inputs: List[dict] = data["inputs"]
        outputs: List[dict] = data["outputs"]

        group = bpy.data.node_groups.new(type="GeometryNodeTree", name=name)

        for input in inputs:
            self.read_input(group, input)

        for output in outputs:
            group.outputs.new(output["type"], output["name"])

        for node in nodes:
            self.read_node(group, node)

        for node in nodes:
            nod = group.nodes[node["name"]]
            inputs = node.get("inputs", [])

            for inp in inputs:
                socket = nod.inputs[inp[0]]

                if len(inp) == 2:
                    if inp[1] is not None and hasattr(socket, "default_value"):
                        socket.default_value = inp[1]
                else:
                    source = group.nodes[inp[1]].outputs[inp[2]]
                    group.links.new(source, socket)

        return group

    def read(
        self, filename: str, opts: Union[str, None] = None
    ) -> Union[
        bpy.types.GeometryNodeTree,
        EffectMetaData,
        Tuple[EffectMetaData, bpy.types.GeometryNodeTree],
    ]:
        with open(filename, "r") as f:
            data: dict = json.load(f)
            if opts is None:
                meta_data: EffectMetaData = self.read_meta_data(data["meta"])
                node_group: bpy.types.GeometryNodeTree = self.read_node_group(
                    data["node_group"]
                )
                return meta_data, node_group
            elif opts == "meta":
                return self.read_meta_data(data["meta"])
            elif opts == "node_group":
                return self.read_node_group(data["node_group"])
            else:
                raise Exception


class EffectWriter:
    def write_meta_data(self, meta_data: EffectMetaData) -> dict:
        data = {
            "name": meta_data.name,
            "description": meta_data.description,
            "author": meta_data.author,
            "icon": meta_data.icon,
            "schema_version": meta_data.schema_version,
            "blender_version": meta_data.blender_version,
            "category": meta_data.categories,
            "subcategory": meta_data.subcategory,
        }
        return data

    def write_node_props(self, node: bpy.types.GeometryNode) -> dict:
        dummy = bpy.data.node_groups.new(type="GeometryNodeTree", name="dummy")
        dumnod = dummy.nodes.new(node.bl_idname)
        props = {}
        for p in dir(node):
            if p == "name":
                continue
            if p == "label":
                continue
            value_n = getattr(node, p)
            if (
                callable(value_n)
                or p.startswith("__")
                or p in EXCLUDE_PROPS
                or node.is_property_readonly(p)
            ):
                continue
            if getattr(dumnod, p) != value_n:
                props["display_in_effect"] = node.gscatter.display_in_effect
                props["display_order"] = node.gscatter.display_order
                props[p] = clean(value_n)

        bpy.data.node_groups.remove(dummy)
        return props

    def write_node(self, node: bpy.types.GeometryNode) -> dict:
        data = {}
        data["type"] = node.bl_idname
        data["name"] = node.name
        data["label"] = node.label

        if isinstance(node, bpy.types.GeometryNodeGroup):
            data["node_group"] = self.write_node_group(node.node_tree)
        else:
            data["props"] = self.write_node_props(node)

        if hasattr(node, "color_ramp"):
            data["color_ramp"] = []
            for c in node.color_ramp.elements:
                data["color_ramp"].append((c.position, list(c.color)))
        elif node.type == "CURVE_FLOAT":
            data["curve_float"] = []
            for p in node.mapping.curves[0].points:
                data["curve_float"].append((tuple(p.location), p.handle_type))

        count = len(node.inputs)
        if isinstance(node, bpy.types.NodeGroupOutput):
            count -= 1
        if count:
            data["inputs"] = []
        for i, inp in zip(range(count), node.inputs):
            if inp.links:
                if node.bl_idname == "GeometryNodeJoinGeometry":
                    inputs.from_join_geometry(data, inp, i)
                else:
                    link: bpy.types.NodeLink = inp.links[0]
                    data["inputs"].append(
                        [
                            i,
                            link.from_node.name,
                            int(link.from_socket.path_from_id().split("[")[-1][:-1]),
                        ]
                    )

            # TODO: Use isinstance instead of bl_idname (after we drop 2.93 support).
            elif inp.bl_idname in NON_PRIMITIVE_SOCKETS:
                data["inputs"].append([i, None])
            else:
                data["inputs"].append([i, clean(inp.default_value)])

        return data

    def write_node_group(self, node_group) -> dict:
        name = node_group.name
        nodes = []
        inputs = []
        outputs = []

        for inp in node_group.inputs.values():
            input = {
                "name": inp.name,
                "type": inp.bl_socket_idname,
            }

            if hasattr(inp, "default_value"):
                input["default"] = clean(inp.default_value)

            if hasattr(inp, "min_value") and inp.min_value > FLOAT_MIN:
                input["min"] = inp.min_value

            if hasattr(inp, "max_value") and inp.max_value < FLOAT_MAX:
                input["max"] = inp.max_value

            inputs.append(input)

        for output in node_group.outputs.values():
            outputs.append(
                {
                    "name": output.name,
                    "type": output.bl_socket_idname,
                }
            )

        for node in node_group.nodes.values():
            nodes.append(self.write_node(node))

        return {"name": name, "nodes": nodes, "inputs": inputs, "outputs": outputs}

    def write(self, meta_data: EffectMetaData, node_group: bpy.types.GeometryNodeTree):
        data = {
            "meta": self.write_meta_data(meta_data),
            "node_group": self.write_node_group(node_group),
        }

        with open(meta_data.filename, "w") as f:
            f.write(json.dumps(data, indent=4))
