from ...utils.logger import debug
from ...common.store import AbstractStoreItem
from typing import Union, Any
import bpy
from .utils import get_input_from_identifier, get_output_from_identifier

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


class Effect(AbstractStoreItem):
    def __init__(
        self,
        id: str,
        name: str,
        author: str,
        description: str,
        icon: str,
        categories: list[str],
        subcategory: str,
        effect_version: list[int],
        schema_version: list[int],
        blender_version: list[int],
        nodetree: Union[dict, bpy.types.GeometryNodeTree],
        blend_types: list[str] = ["ADD", "MULTIPLY", "MIX"],
        default_blend_type: str = "MIX",
    ) -> None:
        super().__init__(id)
        self.name = name
        self.author = author
        self.description = description
        self.icon = icon
        self.categories = categories
        self.subcategory = subcategory
        self.effect_version = effect_version
        self.schema_version = schema_version
        self.blender_version = blender_version
        self.blend_types = blend_types
        self.default_blend_type = default_blend_type
        self._nodetree = {}
        if isinstance(nodetree, bpy.types.GeometryNodeTree):
            self.nodetree = nodetree
        else:
            self._nodetree = nodetree

    @property
    def nodetree(self) -> bpy.types.GeometryNodeTree:
        group = self._node_group_from_dict(self._nodetree, self.name)
        return group

    @nodetree.setter
    def nodetree(self, nodetree: bpy.types.GeometryNodeTree):
        group = self._dict_from_node_group(node_group=nodetree)
        self._nodetree = group

    @property
    def version_str(self):
        str_version = ".".join(map(str, self.effect_version))
        return str_version

    def _node_from_dict(
        self, nodetree: bpy.types.GeometryNodeTree, node_data: list[dict]
    ):
        node = nodetree.nodes.new(node_data["type"])
        node.name = node_data["name"]
        node.label = node_data["label"]

        if isinstance(node, bpy.types.GeometryNodeGroup):
            node.node_tree = self._node_group_from_dict(node_data["node_group"])
            props = node_data.get("props", {})
            for key, value in props.items():
                if key in [
                    "display_in_effect",
                    "display_order",
                    "display_output_as_dropdown",
                    "display_inputs",
                    "display_properties",
                ]:
                    setattr(node.gscatter, key, value)
                elif key == "location":
                    setattr(node, key, value)
        else:
            props = node_data.get("props", {})
            for key, value in props.items():
                if key in [
                    "display_in_effect",
                    "display_order",
                    "display_output_as_dropdown",
                    "display_inputs",
                    "display_properties",
                ]:
                    setattr(node.gscatter, key, value)
                else:
                    if key == "width_hidden":
                        continue
                    try:
                        setattr(node, key, value)
                    except AttributeError as e:
                        debug("Could n't set attribute: %s" % e)

            if "color_ramp" in node_data:
                i = 0
                for pos, color in node_data["color_ramp"][:2]:
                    c = node.color_ramp.elements[i]
                    c.position = pos
                    c.color = color
                    i += 1
                for pos, color in node_data["color_ramp"][2:]:
                    c = node.color_ramp.elements.new(pos)
                    c.color = color
            elif "curve_float" in node_data:
                for i, p in enumerate(node_data["curve_float"][1:-1]):
                    i += 1
                    node.mapping.curves[0].points.new(p[0][0], p[0][1])
                    node.mapping.curves[0].points[i].handle_type = p[1]
                point_first = node_data["curve_float"][0]
                point_last = node_data["curve_float"][-1]
                node.mapping.curves[0].points[0].handle_type = point_first[1]
                node.mapping.curves[0].points[0].location = point_first[0]
                node.mapping.curves[0].points[-1].handle_type = point_last[1]
                node.mapping.curves[0].points[-1].location = point_last[0]

    def _node_group_from_dict(
        self, data: dict, name: str = None
    ) -> bpy.types.GeometryNodeTree:
        name: str = name if name else data["name"]
        nodes: list[dict] = data["nodes"]
        inputs: list[dict] = data["inputs"]
        outputs: list[dict] = data["outputs"]

        group = bpy.data.node_groups.new(type="GeometryNodeTree", name=name)

        # Create node_group inputs sockets
        for input_data in inputs:
            type = input_data["type"]
            sub_type = ""

            # Strip subtype from bl_idname
            socket_types = ("NodeSocketFloat", "NodeSocketInt", "NodeSocketVector")
            for socket_type in socket_types:
                if type.startswith(socket_type):
                    sub_type = type.replace(socket_type, "")
                    type = socket_type
            # debug("Creating NodeSocket", name, input_data["name"], type, "subtype", sub_type)

            try:
                if bpy.app.version >= (4, 0, 0):
                    input = group.interface.new_socket(
                        socket_type=type, name=input_data["name"], in_out="INPUT"
                    )
                    if sub_type != "" and hasattr(input, "subtype"):
                        input.subtype = sub_type.upper()
                else:
                    input = group.inputs.new(type + sub_type, input_data["name"])

                if input_data.get("min") is not None and hasattr(input, "min_value"):
                    input.min_value = input_data["min"]
                if input_data.get("max") is not None and hasattr(input, "max_value"):
                    input.max_value = input_data["max"]
                if input_data.get("default") is not None and hasattr(
                    input, "default_value"
                ):
                    input.default_value = input_data["default"]
                if input_data.get("description") is not None and hasattr(
                    input, "description"
                ):
                    input.description = input_data["description"]
            except Exception as e:
                debug(f"Failed to set Input Socket of {name} {input_data['name']}\n{e}")
                pass

        # Create node_group output sockets
        for output in outputs:
            try:
                if bpy.app.version >= (4, 0, 0):
                    output = group.interface.new_socket(
                        socket_type=output["type"], name=output["name"], in_out="OUTPUT"
                    )
                else:
                    group.outputs.new(output["type"], output["name"])
            except Exception as e:
                debug(f"Failed to create Output Socket of {name} {output['name']}\n{e}")

        # Create Nodes in node_tree
        for node_data in nodes:
            self._node_from_dict(group, node_data)
        for node_data in nodes:
            node: bpy.types.Node = group.nodes[node_data["name"]]
            inputs: list = node_data.get("inputs", [])

            for inp in inputs:
                input_data = dict(enumerate(inp))
                input_socket = input_data.get(0)
                input_default_value = input_data.get(1)
                from_node_name = input_data.get(1)
                from_node_socket = input_data.get(2)

                # Since 4.1 Switch Inputs don't have separate inputs anymore for each input type.
                if isinstance(
                    node, bpy.types.GeometryNodeSwitch
                ) and bpy.app.version >= (4, 1, 0):
                    input_socket = input_socket.split("_")[0]

                if node.type in ["GROUP_INPUT", "GROUP_OUTPUT", "GROUP"]:
                    try:
                        socket = node.inputs[input_socket]
                    except Exception:
                        socket = get_input_from_identifier(node.inputs, input_socket)
                else:
                    socket = get_input_from_identifier(node.inputs, input_socket)

                # if socket is None:
                #     continue

                if len(inp) == 2:  # Has only default_value
                    if input_default_value is not None and hasattr(
                        socket, "default_value"
                    ):
                        try:
                            socket.default_value = clean(input_default_value)
                        except Exception as e:
                            debug(
                                f"Failed to set default_value of node {name} {input_socket} {input_default_value} \n{e}"
                            )
                else:
                    from_node: bpy.types.GeometryNode = group.nodes[from_node_name]
                    if isinstance(
                        from_node, bpy.types.GeometryNodeSwitch
                    ) and bpy.app.version >= (4, 1, 0):
                        from_node_socket = from_node_socket.split("_")[0]
                    if from_node.type in ["GROUP_INPUT", "GROUP_OUTPUT", "GROUP"]:
                        try:
                            source = group.nodes[from_node_name].outputs[
                                from_node_socket
                            ]
                        except Exception:
                            source = get_output_from_identifier(
                                group.nodes[from_node_name].outputs, from_node_socket
                            )
                    else:
                        source = get_output_from_identifier(
                            group.nodes[from_node_name].outputs, from_node_socket
                        )

                    # if source is None:
                    #     continue
                    try:
                        # debug("Input:", node_data["name"], node, input_socket, socket)
                        # debug("From:", from_node_name, from_node, from_node_socket, source)
                        group.links.new(source, socket)
                    except Exception as e:
                        debug(
                            f"Failed to create socket connection {source} {socket}\n {e}"
                        )
        return group

    def _dict_from_node(self, node: bpy.types.GeometryNode) -> dict:
        data = {}
        data["type"] = node.bl_idname
        data["name"] = node.name
        data["label"] = node.label

        if isinstance(node, bpy.types.GeometryNodeGroup):
            data["node_group"] = self._dict_from_node_group(node.node_tree)

        data["props"] = self._dict_from_node_props(node)

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
            count -= 1  # To remove last spare Input
        if count:
            data["inputs"] = []
        for inp in node.inputs:
            inp: bpy.types.NodeSocket
            if inp.enabled:
                if inp.is_linked:
                    link: bpy.types.NodeLink
                    for link in inp.links:
                        data["inputs"].append(
                            [
                                link.to_socket.identifier
                                if node.type
                                not in ["GROUP_INPUT", "GROUP_OUTPUT", "GROUP"]
                                else inp.name,
                                link.from_node.name,
                                link.from_socket.identifier
                                if link.from_node.type
                                not in ["GROUP_INPUT", "GROUP_OUTPUT", "GROUP"]
                                else link.from_socket.name,
                            ]
                        )
                elif hasattr(inp, "default_value"):
                    data["inputs"].append([inp.identifier, clean(inp.default_value)])
                else:
                    data["inputs"].append([inp.identifier, None])
        return data

    def _dict_from_node_props(self, node: bpy.types.GeometryNode) -> dict:
        dummy = bpy.data.node_groups.new(type="GeometryNodeTree", name="dummy")
        dumnod = dummy.nodes.new(node.bl_idname)
        props = {}
        for p in dir(node):
            if p == "name":
                continue
            if p == "label":
                continue
            if p == "node_tree":
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
                props["display_output_as_dropdown"] = (
                    node.gscatter.display_output_as_dropdown
                )
                props["display_order"] = node.gscatter.display_order
                props["display_properties"] = node.gscatter.display_properties
                props["display_inputs"] = node.gscatter.display_inputs
                props[p] = clean(value_n)

        bpy.data.node_groups.remove(dummy)
        return props

    def _dict_from_node_group(self, node_group: bpy.types.GeometryNodeTree) -> dict:
        name = node_group.name
        nodes = []
        inputs = []
        outputs = []

        if bpy.app.version >= (4, 0, 0):
            for item in node_group.interface.items_tree.values():
                data = {
                    "name": item.name,
                    "type": item.socket_type,
                    "identifier": item.identifier,
                    "description": item.description,
                }

                if (
                    hasattr(item, "subtype")
                    and item.subtype is not None
                    and item.subtype != "NONE"
                    and item.subtype != ""
                ):
                    data["type"] = data["type"] + item.subtype.capitalize()

                if hasattr(item, "default_value"):
                    data["default"] = clean(item.default_value)

                if hasattr(item, "min_value") and item.min_value > FLOAT_MIN:
                    data["min"] = item.min_value

                if hasattr(item, "max_value") and item.max_value < FLOAT_MAX:
                    data["max"] = item.max_value

                if item.in_out == "INPUT":
                    inputs.append(data)
                else:
                    outputs.append(data)
        else:
            for inp in node_group.inputs.values():
                input = {
                    "name": inp.name,
                    "type": inp.bl_idname,
                    "identifier": inp.identifier,
                    "description": inp.description,
                }

                if hasattr(inp, "default_value"):
                    input["default"] = clean(inp.default_value)

                if hasattr(inp, "bl_subtype_label"):
                    input["subtype"] = clean(inp.bl_subtype_label)

                if hasattr(inp, "min_value") and inp.min_value > FLOAT_MIN:
                    input["min"] = inp.min_value

                if hasattr(inp, "max_value") and inp.max_value < FLOAT_MAX:
                    input["max"] = inp.max_value

                inputs.append(input)

            for output in node_group.outputs.values():
                outputs.append(
                    {
                        "name": output.name,
                        "type": output.bl_idname,
                        "identifier": output.identifier,
                        "description": output.description,
                    }
                )

        for node in node_group.nodes.values():
            nodes.append(self._dict_from_node(node))

        return {"name": name, "nodes": nodes, "inputs": inputs, "outputs": outputs}

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "author": self.author,
            "description": self.description,
            "icon": self.icon,
            "categories": self.categories,
            "subcategory": self.subcategory,
            "effect_version": self.effect_version,
            "schema_version": self.schema_version,
            "blender_version": self.blender_version,
            "blend_types": self.blend_types,
            "default_blend_type": self.default_blend_type,
            "node_group": self._nodetree,
        }
