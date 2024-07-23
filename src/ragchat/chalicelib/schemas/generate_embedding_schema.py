INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["text"],
    "properties": {"text": {"type": "string", "maxLength": 1000}},
}

OUTPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["vector"],
    "properties": {
        "vector": {"type": "array", "items": {"type": "number"}},
    },
}
