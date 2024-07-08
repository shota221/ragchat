import os
import json
from dataclasses import asdict, dataclass
import boto3
from injector import singleton


@singleton
class StorageClient:
    def __init__(self):
        self.client = boto3.client("s3")
        self.bucket_name = os.environ.get("S3_BUCKET_NAME")

    def exists(self, source_key):
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=source_key)
            return True
        except:
            return False
        
    def list_objects(self):
        response = self.client.list_objects(Bucket=self.bucket_name)
        return response.get("Contents", [])

    def get_json_object(self, source_key):
        obj = self.client.get_object(Bucket=self.bucket_name, Key=source_key)
        json_str = obj["Body"].read().decode("utf-8")
        return json.loads(json_str)

    def put_object(self, source_key, body):
        response = self.client.put_object(
            Bucket=self.bucket_name, Key=source_key, Body=body
        )

        return response
