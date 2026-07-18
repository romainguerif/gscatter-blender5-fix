scatter_system_namespace = {
    "type": "object",
    "properties": {"schema_version": {"type": "array"}, "presets": {"type": "object"}},
}
scatter_system_preset = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "schema_version": {"type": "array"},
        "name": {"type": "string"},
        "is_terrain": {"type": "boolean"},
        "distribution": {
            "type": "array",
        },
        "scale": {
            "type": "array",
        },
        "rotation": {
            "type": "array",
        },
        "geometry": {
            "type": "array",
        },
    },
}
