INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["target_key"],
    "properties": {
        "target_key": {
            "type": "string",
            "description": "チェック対象のドキュメントのS3キー",
        }
    },
}

OUTPUT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["typos"],
    "properties": {
        "typos": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["original", "corrected"],
                "properties": {
                    "original": {
                        "type": "string",
                        "description": "誤字脱字を含む文の抜粋",
                    },
                    "corrected": {"type": "string", "description": "誤字脱字の修正案"},
                },
            },
        },
    },
}
