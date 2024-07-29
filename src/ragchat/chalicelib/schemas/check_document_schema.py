INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["target_key", "checklist"],
    "properties": {
        "target_key": {
            "type": "string",
            "description": "チェック対象のドキュメントのS3キー",
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
        },
        "summary_policy": {"type": "string", "description": "要約の方針"},
    },
}

OUTPUT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["checklist", "typos", "summary"],
    "properties": {
        "checklist": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "result", "quotes", "comment"],
                "properties": {
                    "id": {"type": "string", "description": "チェック項目のID"},
                    "result": {
                        "type": "boolean",
                        "description": "チェック項目に対する回答。回答がYesの場合はtrue、Noもしくはどちらとも言えない場合はfalse",
                    },
                    "quotes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "チェック項目に関連するドキュメントからの引用",
                    },
                    "references": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "チェック項目に関連する図表のタイトル",                        
                    },
                    "comment": {
                        "type": "string",
                        "description": "チェック項目に関するコメント",
                    },
                },
            },
        },
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
        "summary": {"type": "string", "description": "ドキュメントの要約"},
    },
}
