import json
import os
import re
import textwrap
from configparser import ConfigParser
from typing import List
from chalicelib.dataclasses.information_fragment import InformationFragment
from chalicelib.schemas import generation_ai_doc_check_schema


class PromptBuilder:
    def __init__(self, config: ConfigParser = None):
        if config:
            self.config = config
        else:
            self.config = ConfigParser()
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.ini")
            self.config.read(filepath, encoding="utf-8")

    def build_inquiry_prompt(
        self,
        inquiry: str,
        informations: List[InformationFragment],
        section: str = "INQUIRY",
    ) -> str:
        config = self.config[section]

        preface = config.get("Preface", "").strip()

        rules = config.get("Rules", "").strip().splitlines()

        rule_prompts = ""

        for rule in rules:
            rule_prompts = rule_prompts + "・" + rule + "\n"

        information_prompts = ""

        for information in informations:
            information_prompts = (
                information_prompts
                + "情報:「"
                + information.text
                + "」（出典:"
                + information.source
                + "）\n"
            )

        if not information_prompts:
            information_prompts = "情報: なし"

        prompt = f"""

    {preface}

    ルール:
    {rule_prompts}

    {information_prompts}

    問い合わせ:「{inquiry}」 """

        print(prompt)

        return prompt

    def build_doc_check_prompt(
        self,
        document: str,
        checklist: str,
        policy: str = None,
        section: str = "DOC_CHECK",
    ) -> str:
        config = self.config[section]
        prompt_format = config.get("Format", "")
        schema = json.dumps(
            generation_ai_doc_check_schema.ASSISTANT, ensure_ascii=False
        )

        return self.__fill_in_xml(
            prompt_format,
            document=document,
            checklist=checklist,
            schema=schema,
            policy=policy,
        )

    def __fill_in_xml(self, prompt_format, **kwargs):
        prompt = textwrap.dedent(prompt_format).strip()
        for key, value in kwargs.items():
            prompt = re.sub(rf"<{key}>\s*</{key}>", f"<{key}>{value}</{key}>", prompt)
        return prompt
