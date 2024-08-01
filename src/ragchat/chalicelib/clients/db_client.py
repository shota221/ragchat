import boto3
from injector import singleton

@singleton
class DBClient:
    def __init__(self):
        self.client = boto3.client("dynamodb")
    
    def get_item(self, table_name, key):
        response = self.client.get_item(
            TableName=table_name,
            Key=key
        )
        return response.get("Item", {})
    
    def put_item(self, table_name, item):
        response = self.client.put_item(
            TableName=table_name,
            Item=item
        )
        return response
    
    def delete_item(self, table_name, key):
        response = self.client.delete_item(
            TableName=table_name,
            Key=key
        )
        return response