DOC_TYPO_CHECK = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "org": {
                "type": "string",
                # "maxLength": 20,
                "description": "ドキュメントから誤字脱字を含む文節をそのまま抜粋してください。",
            },
            "cor": {
                "type": "string",
                "description": "誤字脱字の修正案を記入してください。",
            },
        },
        "required": ["org", "cor"],
    },
    "description": "ドキュメントから誤字脱字を注意深く見つけてすべて列挙してください。誤字脱字がない場合は、空の配列を記入してください。チェックリスト内の誤字脱字は無視してください。",
}

DOC_CHECKLIST_CHECK = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    # "maxItems": 10,
    "items": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "チェック項目のうち、回答がNoであるチェック項目のIDを記入してください。このIDは、与えられたチェックリストのIDと一致している必要があります。",
            },
            "qot": {
                "type": "string",
                "description": "チェック項目に関連する文をドキュメントからそのまま抜粋してください。該当文が100文字を超える場合は文頭の100文字を抜粋してください。",
            },
            "cmt": {
                "type": "string",
                "description": "チェック項目に関するコメントを記入してください。",
            },
        },
        "required": ["id", "qot", "cmt"],
        "description": "チェックリスト内のチェック項目のうち、回答がNoであるチェック項目に関する情報を列挙してください。回答がYesのチェック項目に関する情報は無視してください。",
    },
}

DOC_CONSISTENCY_CHECK = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    # "maxItems": 10,
    "items": {
        "type": "object",
        "properties": {
            "qot": {
                "type": "string",
                "description": "矛盾している箇所をdocumentタグ内からそのまま抜粋してください。",
            },
            "cmt": {
                "type": "string",
                "description": "矛盾している箇所に関するコメントを記入してください。その際、「参考文書には～と記述されているが、ドキュメントには～と記述されている箇所がある。」といった形式で記入してください。",
            },
        },
        "required": ["qot", "cmt"],
        "description": "documentタグ内の記述に関して、referenceタグ内の記述と明らかに矛盾している箇所を注意深く見つけてすべて列挙してください。整合性が取れていない箇所がない場合は、空の配列を記入してください。",
    },
}

# ASSISTANT = {
#     "$schema": "http://json-schema.org/draft-07/schema#",
#     "type": "object",
#     "properties": {
#         "checklist": {
#             "type": "array",
#             # "maxItems": 10,
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "id": {
#                         "type": "string",
#                         "description": "チェック項目のIDを記入してください。このIDは、与えられたチェックリストのIDと一致している必要があります。",
#                     },
#                     "res": {
#                         "type": "boolean",
#                         "description": "チェック項目に対して回答してください。回答がYesの場合はtrue、Noもしくはどちらとも言えない場合はfalseを記入してください。",
#                     },
#                     "qot": {
#                         "type": "array",
#                         # "maxItems": 3,
#                         "items": {
#                             "type": "string"
#                             # , "maxLength": 100
#                         },
#                         "description": "チェック項目に関連する文をドキュメントからそのまま抜粋してください。該当文が100文字を超える場合は文頭の100文字を抜粋してください。複数存在する場合は最大3箇所まで記入してください。該当箇所がない場合は、空の配列を記入してください。",
#                     },
#                     "cmt": {
#                         "type": "string",
#                         "description": "チェック項目に関するコメントを記入してください。コメントは、チェック項目の回答がfalse (Noまたはどちらとも言えない)の場合に必須です。",
#                     },
#                 },
#                 "required": ["id", "res", "qot", "cmt"],
#                 "description": "ドキュメントについてチェックリストの各項目に対して回答してください。",
#             },
#         },
#         "typos": {
#             "type": "array",
#             # "maxItems": 20,
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "org": {
#                         "type": "string",
#                         # "maxLength": 20,
#                         "description": "ドキュメントから誤字脱字を含む文節をそのまま抜粋してください。チェックリスト内の誤字脱字は無視してください。",
#                     },
#                     "cor": {
#                         "type": "string",
#                         "description": "誤字脱字の修正案を記入してください。",
#                     },
#                 },
#                 "required": ["org", "cor"],
#             },
#             "description": "ドキュメントから誤字脱字を注意深く見つけてすべて列挙してください。誤字脱字がない場合は、空の配列を記入してください。チェックリスト内の誤字脱字は無視してください。",
#         },
#     },
#     "required": ["checklist", "typos", "summary", "protocol_violations"],
# }