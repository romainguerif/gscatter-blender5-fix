effect = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "author": {"type": "string"},
        "description": {"type": "string"},
        "icon": {"type": "string"},
        "categories": {"type": "array"},
        "subcategory": {"type": "string"},
        "effect_version": {"type": "array"},
        "schema_version": {"type": "array"},
        "blender_version": {"type": "array"},
        "node_group": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "nodes": {"type": "array"},
                "inputs": {"type": "array"},
                "outputs": {"type": "array"},
            },
        },
    },
}
effect_preset = {
    "type": "object",
    "properties": {
        "id": {"type": "str"},
        "name": {"type": "str"},
        "schema_version": {"type": "array"},
        "effect_id": {"type": "str"},
        "params": {"type": "str"},
        "layer_params": {"type": "str"},
    },
}
effect_preset_namespace = {
    "type": "object",
    "properties": {"schema_version": {"type": "array"}, "presets": {"type": "object"}},
}
effect_namespace = {
    "type": "object",
    "properties": {
        "version": {"type": "array"},
        "authors": {"type": "object", "properties": {"effects": {"type": "object"}}},
    },
}
