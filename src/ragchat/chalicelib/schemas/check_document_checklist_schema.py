INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["target_key", "checklist"],
    "properties": {
        "target_key": {
            "type": "string",
            "description": "チェック対象のドキュメントのS3キー",
        },
        "reference_key": {
            "type": "string",
            "description": "参考文書のS3キー",
        },
        "checklist": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "text"],
                "properties": {
                    "id": {"type": "string", "description": "チェック項目ID"},
                    "text": {"type": "string", "description": "チェック項目の内容"},
                },
            },
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
                "required": ["id", "result", "quote", "comment"],
                "properties": {
                    "id": {"type": "string", "description": "チェック項目のID"},
                    "result": {
                        "type": "string",
                        "description": "回答がYesである場合は'Y'、Noもしくはどちらとも言えない場合は'N'",
                    },
                    "quote": {
                        "type": "string",
                        "description": "チェック項目に関連するドキュメントからの引用",
                    },
                    "comment": {
                        "type": "string",
                        "description": "チェック項目に関するコメント",
                    },
                },
            },
        }
    },
}
