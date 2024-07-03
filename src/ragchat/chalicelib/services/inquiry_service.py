import configparser
import json
from configparser import ConfigParser
import boto3
from injector import inject
from aws_lambda_powertools.utilities.validation import validate
from chalicelib.helper import result_handler, PromptBuilder
from chalicelib.clients.generation_ai_client import GenerationAiClient
from chalicelib.clients.search_engine_client import (
    SearchEngineClient,
    SearchCondition,
    DataSourceSyncJobListCondition,
)
from chalicelib.schemas import send_inquiry_schema


class InquiryService:
    @inject
    def __init__(
        self,
        search_engine_client: SearchEngineClient,
        generation_ai_client: GenerationAiClient,
    ):
        self.generation_ai_client = generation_ai_client
        self.search_engine_client = search_engine_client

    @result_handler
    def send(self, json_body):
        validate(event=json_body, schema=send_inquiry_schema.INPUT)

        config = ConfigParser()
        config.read("prompt.ini", encoding='utf-8')

        prompt_builder = PromptBuilder(config)

        information_fragments = self.search_engine_client.search(
            SearchCondition(query_text=json_body["userText"])
        )

        prompt = prompt_builder.build(
            inquiry=json_body["userText"],
            informations=information_fragments,
        )

        response = self.generation_ai_client.generate_message(prompt)
        return response
