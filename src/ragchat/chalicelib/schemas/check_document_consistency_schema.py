INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["target_key", "reference_key"],
    "properties": {
        "target_key": {
            "type": "string",
            "description": "チェック対象のドキュメントのS3キー",
        },
        "reference_key": {
            "type": "string",
            "description": "参考文書のS3キー",
        }
    },
}

OUTPUT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "comments": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["quote", "comment"],
                "properties": {
                    "quote": {
                        "type": "string",
                        "description": "参考文書と不整合があると思われる箇所に関連するドキュメントからの引用",
                    },
                    "comment": {
                        "type": "string",
                        "description": "参考文書と不整合があると思われる箇所に関するコメント",
                    },
                },
            },
        }
    },
}
