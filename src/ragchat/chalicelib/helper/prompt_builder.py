from configparser import ConfigParser
from typing import List
from chalicelib.dataclasses.information_fragment import InformationFragment


class PromptBuilder:
    def __init__(self, config: ConfigParser):
        self.config = config

    def build(
        self, inquiry: str, informations: List[InformationFragment], section: str = "v1"
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

        prompt = f"""

    {preface}

    ルール:
    {rule_prompts}

    {information_prompts}

    質問:「{inquiry}」 """
        
        print(prompt)

        return prompt
