import configparser
import os
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
from chalicelib.dataclasses.send_inquiry_result import SendInquiryResult
from chalicelib.dataclasses.generate_embedding_result import GenerateEmbeddingResult
from chalicelib.schemas import send_inquiry_schema, generate_embedding_schema


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
        dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(dir, 'prompt.ini')
        config.read(filepath, encoding='utf-8')

        prompt_builder = PromptBuilder(config)

        query_text = json_body["user_text"]  
        source_uris = json_body.get("conditions", {}).get("source_uris", [])
        category_ids = json_body.get("conditions", {}).get("category_ids", [])

        information_fragments = self.search_engine_client.search(
            SearchCondition(query_text=query_text, source_uris=source_uris, category_ids=[str(v) for v in category_ids])
        )

        prompt = prompt_builder.build(
            inquiry=json_body["user_text"],
            informations=information_fragments,
        )

        assistant_text = self.generation_ai_client.generate_message(prompt)

        user_text_embedding = self.generation_ai_client.generate_embedding(query_text)

        return SendInquiryResult(assistant_text=assistant_text, vectors={"user_text": user_text_embedding})
    
    @result_handler
    def generate_embedding(self, json_body):
        validate(event=json_body, schema=generate_embedding_schema.INPUT)

        embedding = self.generation_ai_client.generate_embedding(json_body["text"])

        return GenerateEmbeddingResult(vector=embedding)