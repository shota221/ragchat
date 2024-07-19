import os
import time
from chalice.test import Client
from pytest import fixture
from app import app

LAMBDA_NAME = ""
FILE_NAME = "サンプルPDF.pdf"


@fixture(name="test_client")
def fixture_client():
    with Client(app) as client:
        yield client


def test_split(test_client):
    # 所要時間計測
    print(f"start: {time.time()}")
    response = test_client.lambda_.invoke(
        "on_s3_object_created",
        test_client.events.generate_s3_event(
            bucket=os.environ["S3_SOURCE_BUCKET_NAME"],
            key=FILE_NAME,
            event_name="s3:ObjectCreated:*",
        ),
    )
    print(f"end: {time.time()}")
    assert response

# def test_delete(test_client):
#     response = test_client.lambda_.invoke(
#         "on_s3_object_removed",
#         test_client.events.generate_s3_event(
#             bucket=os.environ["S3_SOURCE_BUCKET_NAME"],
#             key=FILE_NAME,
#             event_name="s3:ObjectRemoved:Delete",
#         ),
#     )
#     assert response