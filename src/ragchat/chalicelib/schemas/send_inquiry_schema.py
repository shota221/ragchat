INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["user_text"],
    "properties": {
        "user_text": {"type": "string"},
        "conditions": {
            "type": "object",
            "properties": {
                "source_uris": {"type": "array"},
                "categories": {"type": "array"},
            },
        }
    },
}
