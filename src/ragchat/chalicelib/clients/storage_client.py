import os
import json
from dataclasses import asdict, dataclass
import boto3
from injector import singleton


@singleton
class StorageClient:
    def __init__(self):
        self.client = boto3.client("s3")
        self.resource = boto3.resource("s3")

    def exists(self, bucket, key):
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except:
            return False
        
    def exists_dir(self, bucket, dir):
        if dir and not dir.endswith("/"):
            raise ValueError("dir must end with /")
        response = self.list_objects(bucket, dir)
        return len(response) > 0

    def list_objects(self, bucket, prefix=''):
        response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return response.get("Contents", [])

    def get_json_object(self, bucket, key):
        obj = self.client.get_object(Bucket=bucket, Key=key)
        json_str = obj["Body"].read().decode("utf-8")
        return json.loads(json_str)
    
    def get_pdf_object(self, bucket, key):
        obj = self.client.get_object(Bucket=bucket, Key=key)
        pdf_bytes = obj["Body"].read()
        return pdf_bytes

    def put_object(self, bucket, key, body):
        response = self.client.put_object(
            Bucket=bucket, Key=key, Body=body
        )
        return response
    
    def copy_object(self, bucket, key, destination_bucket, destination_key):
        response = self.client.copy_object(
            Bucket=destination_bucket,
            Key=destination_key,
            CopySource={"Bucket": bucket, "Key": key},
        )
        return response

    def delete_object(self, bucket, key):
        response = self.client.delete_object(Bucket=bucket, Key=key)
        return response
    
    def delete_objects(self, bucket, prefix):
        bucket = self.resource.Bucket(bucket)
        response = bucket.objects.filter(Prefix=prefix).delete()
        return response