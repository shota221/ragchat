from chalice.test import Client
from pytest import fixture
from app import app

LAMBDA_NAME = ""


@fixture(name="test_client")
def fixture_client():
    with Client(app) as client:
        yield client
