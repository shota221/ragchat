import os
import json
from injector import inject
from aws_lambda_powertools.utilities.validation import validate
from chalicelib.helper import result_handler
from chalicelib.clients.storage_client import StorageClient
from chalicelib.schemas import update_file_attr_schema
from chalicelib.helper import file_util


class FileAttrService:
    S3_SOURCE_BUCKET_NAME = os.environ["S3_SOURCE_BUCKET_NAME"]
    S3_DESTINATION_BUCKET_NAME = os.environ["S3_DESTINATION_BUCKET_NAME"]

    @inject
    def __init__(self, storage_client: StorageClient):
        self.storage_client = storage_client

    @result_handler
    def update(self, json_body):
        validate(event=json_body, schema=update_file_attr_schema.INPUT)

        for item in json_body:
            target_key = item["file_name"]

            if not self.storage_client.exists(self.S3_SOURCE_BUCKET_NAME, target_key):
                raise Exception(f"File not found: {target_key}")

        results = []

        for item in json_body:
            target_key = item["file_name"]

            meta_file_dir = file_util.guess_meta_dir(target_key)
            attributes = item["attributes"]

            meta_objects = self.storage_client.list_objects(
                self.S3_DESTINATION_BUCKET_NAME, meta_file_dir
            )

            if meta_objects:
                for obj in meta_objects:
                    meta_key = obj["Key"]
                    if not file_util.is_meta_file(meta_key):
                        continue
                    meta = self.storage_client.get_json_object(
                        self.S3_DESTINATION_BUCKET_NAME, meta_key
                    )
                    meta = file_util.overwrite_meta(meta, attributes)
                    result = self.storage_client.put_object(
                        self.S3_DESTINATION_BUCKET_NAME,
                        meta_key,
                        json.dumps(meta, ensure_ascii=False),
                    )
                    print(f"meta_key: {meta_key} updated")
            else:
                meta = file_util.generate_meta(target_key, attributes)
                meta_key = file_util.guess_tmp_meta_key(target_key)
                result = self.storage_client.put_object(
                    self.S3_DESTINATION_BUCKET_NAME,
                    meta_key,
                    json.dumps(meta, ensure_ascii=False),
                )

            results.append(result)

        return results
