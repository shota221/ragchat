ASSISTANT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "checklist": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "チェック項目のIDを記入してください。このIDは、与えられたチェックリストのIDと一致している必要があります。"
                    },
                    "res": {
                        "type": "boolean",
                        "description": "チェック項目に対して回答してください。回答がYesの場合はtrue、Noもしくはどちらとも言えない場合はfalseを記入してください。"
                    },
                    "qot": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "チェック項目に関連する文をドキュメントからそのまま抜粋してください。複数存在する場合は最大3箇所まで記入してください。該当箇所がない場合は、空の配列を記入してください。"
                    },
                    "ref": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "チェック項目に関連する図表のタイトルをドキュメントからそのまま抜粋してください。複数存在する場合は最大3箇所まで記入してください。該当箇所がない場合は、空の配列を記入してください。"
                    },
                    "cmt": {
                        "type": "string",
                        "description": "チェック項目に関するコメントを記入してください。コメントは、チェック項目の回答がfalse (Noまたはどちらとも言えない)の場合に必須です。"
                    }
                },
                "required": ["id", "res", "qot", "ref", "cmt"],
                "description": "ドキュメントについてチェックリストの各項目に対して回答してください。"
            }
        },
        "typos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "org": {
                        "type": "string",
                        "description": "ドキュメントから誤字脱字を含む一文を文頭から文末までそのまま抜粋してください。チェックリスト内の誤字脱字は無視してください。"
                    },
                    "cor": {
                        "type": "string",
                        "description": "誤字脱字を修正した一文を記入してください。"
                    }
                },
                "required": ["org", "cor"]
            },
            "description": "ドキュメントから誤字脱字を注意深く見つけてすべて列挙してください。誤字脱字がない場合は、空の配列を記入してください。チェックリスト内の誤字脱字は無視してください。"
        },
        "summary": {
            "type": "string",
            "description": "ドキュメントの内容を簡潔に要約してください。policyタグ内のjsonに$.summaryがある場合はそれに従ってください。また、ドキュメント中で明確に記載されていない内容は決して記入しないでください。"
        }
    },
    "required": ["checklist", "typos", "summary"]
}
