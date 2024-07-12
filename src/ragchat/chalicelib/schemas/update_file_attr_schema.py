INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "array",
    "items": {
        "type": "object",
        "required": ["file_name", "attributes"],
        "properties": {
            "file_name": {"type": "string"},
            "attributes": {
                "type": "object",
                "properties": {"category_ids": {"type": "array"}},
            },
        },
    },
}
