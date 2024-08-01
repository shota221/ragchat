import os
import json
from dataclasses import asdict, dataclass
import boto3
from botocore.config import Config
from injector import singleton


@singleton
class GenerationAiClient:
    def __init__(self):
        self.bedrock_model_id = os.environ.get("BEDROCK_MODEL_ID")
        self.embedding_model_id = os.environ.get("BEDROCK_EMBEDDING_MODEL_ID")
        bedrock_config = Config(
            region_name=os.environ.get("BEDROCK_REGION"),
        )
        self.client = boto3.client("bedrock-runtime", config=bedrock_config)

    def generate_message(self, user_text, assistant_text = None, max_tokens=1000, temperature= 1, top_p=0.999):
        response = self.client.invoke_model(
            modelId=self.bedrock_model_id,
            accept="application/json",
            contentType="application/json",
            body=self.__generate_invoke_model_body(user_text, assistant_text, max_tokens, temperature, top_p),
        )

        response_body = json.loads(response["body"].read().decode("utf-8"))

        print(json.dumps(response_body["usage"]))

        return response_body["content"][0]["text"]

    def generate_embedding(self, text):
        body = json.dumps(
            {
                "inputText": text,
            }
        ).encode("utf-8")

        response = self.client.invoke_model(
            modelId=self.embedding_model_id,
            accept="*/*",
            contentType="application/json",
            body=body,
        )

        response_body = json.loads(response.get("body").read())

        embedding = response_body.get("embedding")

        return embedding


    def stream_message(self, user_text):
        bedrock_response = self.client.invoke_model_with_response_stream(
            modelId=self.bedrock_model_id,
            body=self.__generate_invoke_model_body(user_text),
        )

        return bedrock_response.get('body')

    def __generate_invoke_model_body(self, user_text, assistant_text = None, max_tokens=1000, temperature= 1, top_p=0.999):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": user_text}]},
        ]
        if assistant_text:
            messages.append(
                {"role": "assistant", "content": [{"type": "text", "text": assistant_text}]}
            )
        return json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
                "top_p": top_p,
            }
        )