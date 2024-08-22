import os
import json
import boto3
from injector import inject
from aws_lambda_powertools.utilities.validation import validate
from chalicelib.helper import result_handler, PromptBuilder
from chalicelib.clients.generation_ai_client import GenerationAiClient
from chalicelib.clients.search_engine_client import (
    SearchEngineClient,
    SearchCondition
)
from chalicelib.dataclasses.send_inquiry_result import SendInquiryResult
from chalicelib.dataclasses.generate_embedding_result import GenerateEmbeddingResult
from chalicelib.schemas import send_inquiry_schema, generate_embedding_schema


class InquiryService:
    FINAL_CHUNK = "[END]"

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

        prompt_builder = PromptBuilder()

        user_group_id = json_body["user_group_id"]
        query_text = json_body["user_text"]  
        file_keys = json_body.get("conditions", {}).get("file_keys", [])
        category_ids = json_body.get("conditions", {}).get("category_ids", [])

        information_fragments = self.search_engine_client.search(
            user_group_id,
            SearchCondition(query_text=query_text, file_keys=file_keys, category_ids=[str(v) for v in category_ids])
        )

        prompt = prompt_builder.build_inquiry_prompt(
            inquiry=json_body["user_text"],
            informations=information_fragments,
        )

        print(f"prompt: {prompt}")

        assistant_text = self.generation_ai_client.generate_message(prompt)

        user_text_embedding = self.generation_ai_client.generate_embedding(query_text)

        return SendInquiryResult(assistant_text=assistant_text, vectors={"user_text": user_text_embedding})
    
    @result_handler
    def generate_embedding(self, json_body):
        validate(event=json_body, schema=generate_embedding_schema.INPUT)

        embedding = self.generation_ai_client.generate_embedding(json_body["text"])

        return GenerateEmbeddingResult(vector=embedding)
    

    def stream(self, json_body):
        validate(event=json_body, schema=send_inquiry_schema.INPUT)

        prompt_builder = PromptBuilder()

        user_group_id = json_body["user_group_id"]
        query_text = json_body["user_text"]  
        file_keys = json_body.get("conditions", {}).get("file_keys", [])
        category_ids = json_body.get("conditions", {}).get("category_ids", [])

        information_fragments = self.search_engine_client.search(
            user_group_id,
            SearchCondition(query_text=query_text, file_keys=file_keys, category_ids=[str(v) for v in category_ids])
        )

        prompt = prompt_builder.build_inquiry_prompt(
            inquiry=json_body["user_text"],
            informations=information_fragments,
        )

        print(f"prompt: {prompt}")

        for event in self.generation_ai_client.stream_message(prompt):
            chunk = json.loads(event.get('chunk').get('bytes'))
            if chunk.get('type') == 'content_block_delta' and chunk.get('delta').get('type') == 'text_delta':
                content = chunk.get('delta').get('text')
                if content:
                    yield content
        yield self.FINAL_CHUNK
