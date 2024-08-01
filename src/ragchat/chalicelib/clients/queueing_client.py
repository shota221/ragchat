import os
import boto3
from injector import singleton

@singleton
class QueueingClient:
    def __init__(self):
        self.client = boto3.client("sqs")

    def send_message(self, queue_name, message_body):
        response = self.client.send_message(
            QueueUrl=self.__queue_url(queue_name),
            MessageBody=message_body            
        )
        return response        


    def __queue_url(self, queue_name):
        queue_url = self.client.get_queue_url(QueueName=queue_name)["QueueUrl"]
        return queue_url