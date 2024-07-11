INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["text"],
    "properties": {"text": {"type": "string"}},
}

OUTPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["vector"],
    "properties": {
        "vector": {"type": "array", "items": {"type": "number"}},
    },
}
