import json
import os
import re
import textwrap
from dataclasses import asdict
from configparser import ConfigParser
from typing import List
from chalicelib.dataclasses.information_fragment import InformationFragment
from chalicelib.schemas import generation_ai_schema


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
        promprt_format = config.get("Format", "")
        rules = config.get("Rules", "").strip().splitlines()

        return self.__fill_in_xml(
            promprt_format,
            informations=json.dumps([asdict(info) for info in informations], ensure_ascii=False),
            rules=json.dumps(rules, ensure_ascii=False),
            inquiry=inquiry
        )

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
            generation_ai_schema.ASSISTANT, ensure_ascii=False
        )

        return self.__fill_in_xml(
            prompt_format,
            document=document,
            checklist=checklist,
            schema=schema,
            policy=policy,
        )
    
    def build_doc_typo_check_prompt(
            self,
            document: str,
            section: str = "DOC_TYPO_CHECK",
    ) -> str:
        config = self.config[section]
        prompt_format = config.get("Format", "")
        schema = json.dumps(
            generation_ai_schema.DOC_TYPO_CHECK, ensure_ascii=False
        )

        return self.__fill_in_xml(
            prompt_format,
            document=document,
            schema=schema,
        )
    
    def build_doc_checklist_check_prompt(
            self,
            document: str,
            checklist: str,
            section: str = "DOC_CHECKLIST_CHECK",
    ) -> str:
        config = self.config[section]
        prompt_format = config.get("Format", "")
        schema = json.dumps(
            generation_ai_schema.DOC_CHECKLIST_CHECK, ensure_ascii=False
        )

        return self.__fill_in_xml(
            prompt_format,
            document=document,
            checklist=checklist,
            schema=schema,
        )
    
    def build_doc_checklist_check_with_reference_prompt(
            self,
            document: str,
            checklist: str,
            reference: str,
            section: str = "DOC_CHECKLIST_CHECK_WITH_REFERENCE",
    ) -> str:
        config = self.config[section]
        prompt_format = config.get("Format", "")
        schema = json.dumps(
            generation_ai_schema.DOC_CHECKLIST_CHECK, ensure_ascii=False
        )

        return self.__fill_in_xml(
            prompt_format,
            document=document,
            checklist=checklist,
            reference=reference,
            schema=schema,
        )

    def build_doc_consistency_check_prompt(
            self,
            document: str,
            reference: str,
            section: str = "DOC_CONSISTENCY_CHECK",
    ) -> str:
        config = self.config[section]
        prompt_format = config.get("Format", "")
        schema = json.dumps(
            generation_ai_schema.DOC_CONSISTENCY_CHECK, ensure_ascii=False
        )

        return self.__fill_in_xml(
            prompt_format,
            document=document,
            reference=reference,
            schema=schema,
        )

    def __fill_in_xml(self, prompt_format, **kwargs):
        prompt = textwrap.dedent(prompt_format).strip()
        for key, value in kwargs.items():
            prompt = re.sub(rf"<{key}>\s*</{key}>", f"<{key}>{value}</{key}>", prompt)
        return prompt
