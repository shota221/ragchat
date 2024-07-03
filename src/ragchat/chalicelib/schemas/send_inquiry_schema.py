INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["userText"],
    "properties": {
        "userText": {"type": "string"},
        "conditions": {
            "type": "object",
            "properties": {
                "sourceUris": {"type": "array"},
                "categories": {"type": "array"},
            },
        }
    },
}
