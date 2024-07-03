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
        bedrock_config = Config(
            region_name=os.environ.get("BEDROCK_REGION"),
        )
        self.client = boto3.client("bedrock-runtime", config=bedrock_config)

    def generate_message(self, user_text):
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": user_text}]}
                ],
            }
        )

        response = self.client.invoke_model(
            modelId=self.bedrock_model_id,
            accept="application/json",
            contentType="application/json",
            body=body,
        )

        response_body = json.loads(response["body"].read().decode("utf-8"))

        return response_body["content"][0]["text"]
