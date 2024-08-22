INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "array",
    "items": {
        "type": "object",
        "required": ["file_key", "attributes"],
        "properties": {
            "file_key": {"type": "string"},
            "attributes": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string"},
                    "category_ids": {"type": "array"},
                    "group_ids": {"type": "array"},
                },
            },
        },
    },
}