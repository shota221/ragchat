import os
import json
from datetime import datetime
import urllib.parse
import boto3
from injector import inject
from aws_lambda_powertools.utilities.validation import validate
from chalicelib.helper import result_handler
from chalicelib.clients.storage_client import StorageClient
from chalicelib.schemas import update_file_attr_schema


class FileAttrService:
    META_FILE_PREFIX = "meta/"
    META_FILE_SUFFIX = ".metadata.json"
    HTTP_FILE_URI_PREFIX = (
        "https://s3-"
        + os.environ["AWS_DEFAULT_REGION"]
        + ".amazonaws.com/"
        + os.environ["S3_BUCKET_NAME"]
        + "/"
    )
    HTTP_FILE_URI_PREFIX_2 = (
        "https://"
        + os.environ["S3_BUCKET_NAME"]
        + ".s3."
        + os.environ["AWS_DEFAULT_REGION"]
        + ".amazonaws.com/"
    )
    S3_FILE_URI_PREFIX = "s3://" + os.environ["S3_BUCKET_NAME"] + "/"

    @inject
    def __init__(self, storage_client: StorageClient):
        self.storage_client = storage_client

    @result_handler
    def update(self, json_body):
        validate(event=json_body, schema=update_file_attr_schema.INPUT)

        for item in json_body:
            target_key = item["file_name"]

            if not self.storage_client.exists(target_key):
                raise Exception(f"File not found: {target_key}")

        results = []

        for item in json_body:
            target_key = item["file_name"]

            meta_file_key = self.META_FILE_PREFIX + target_key + self.META_FILE_SUFFIX
            attributes = item["attributes"]

            if self.storage_client.exists(meta_file_key):
                meta = self.storage_client.get_json_object(meta_file_key)
            else:
                http_file_uri = self.HTTP_FILE_URI_PREFIX + target_key
                http_encoded_file_uri = self.HTTP_FILE_URI_PREFIX + urllib.parse.quote(
                    target_key
                )
                http_file_uri_2 = self.HTTP_FILE_URI_PREFIX_2 + target_key
                http_encoded_file_uri_2 = (
                    self.HTTP_FILE_URI_PREFIX_2 + urllib.parse.quote(target_key)
                )
                s3_file_uri = self.S3_FILE_URI_PREFIX + target_key
                s3_encoded_file_uri = self.S3_FILE_URI_PREFIX + urllib.parse.quote(
                    target_key
                )
                meta = {
                    "Attributes": {
                        "source_uris": [
                            http_file_uri,
                            http_encoded_file_uri,
                            http_file_uri_2,
                            http_encoded_file_uri_2,
                            s3_file_uri,
                            s3_encoded_file_uri,
                        ]
                    }
                }

            for key, value in attributes.items():
                if isinstance(value, list):
                    attributes[key] = [str(v) for v in value]
                meta["Attributes"][key] = attributes[key]

            result = self.storage_client.put_object(
                meta_file_key, json.dumps(meta, ensure_ascii=False)
            )

            results.append(result)

        return results

    @result_handler
    def init(self):
        targets = self.storage_client.list_objects()
        target_keys = [obj["Key"] for obj in targets]
        for target_key in target_keys:
            if target_key.startswith(self.META_FILE_PREFIX):
                continue
            meta_file_key = self.META_FILE_PREFIX + target_key + self.META_FILE_SUFFIX
            http_file_uri = self.HTTP_FILE_URI_PREFIX + target_key
            http_encoded_file_uri = self.HTTP_FILE_URI_PREFIX + urllib.parse.quote(
                target_key
            )
            http_file_uri_2 = self.HTTP_FILE_URI_PREFIX_2 + target_key
            http_encoded_file_uri_2 = self.HTTP_FILE_URI_PREFIX_2 + urllib.parse.quote(
                target_key
            )
            s3_file_uri = self.S3_FILE_URI_PREFIX + target_key
            s3_encoded_file_uri = self.S3_FILE_URI_PREFIX + urllib.parse.quote(
                target_key
            )
            if self.storage_client.exists(meta_file_key):
                meta = self.storage_client.get_json_object(meta_file_key)
                meta["Attributes"]["source_uris"] = [
                    http_file_uri,
                    http_encoded_file_uri,
                    http_file_uri_2,
                    http_encoded_file_uri_2,
                    s3_file_uri,
                    s3_encoded_file_uri,
                ]
            else:
                meta = {
                    "Attributes": {
                        "source_uris": [
                            http_file_uri,
                            http_encoded_file_uri,
                            http_file_uri_2,
                            http_encoded_file_uri_2,
                            s3_file_uri,
                            s3_encoded_file_uri,
                        ]
                    }
                }
            self.storage_client.put_object(
                meta_file_key, json.dumps(meta, ensure_ascii=False)
            )
        return {"status": "ok"}

    def remove(self, target_key):
        if target_key.startswith(self.META_FILE_PREFIX):
            return
        if self.storage_client.exists(target_key):
            return
        meta_file_key = self.META_FILE_PREFIX + target_key + self.META_FILE_SUFFIX
        if self.storage_client.exists(meta_file_key):
            self.storage_client.delete_object(meta_file_key)
        return
