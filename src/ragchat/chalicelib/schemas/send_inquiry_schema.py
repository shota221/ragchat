INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["user_text"],
    "properties": {
        "user_text": {
            "type": "string",
            "maxLength": 1000
            },
        "conditions": {
            "type": "object",
            "properties": {
                "source_uris": {
                    "type": "array",
                    "maxItems": 10,
                    "items": {"type": "string"},
                },
                "category_ids": {"type": "array", "maxItems": 10},
            },
        },
    },
}

OUTPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["assistant_text", "vector"],
    "properties": {
        "assistant_text": {"type": "string"},
        "vectors": {
            "type": "object",
            "required": ["user_text"],
            "properties": {
                "user_text": {"type": "array", "items": {"type": "number"}},
            },
        },
    },
}
