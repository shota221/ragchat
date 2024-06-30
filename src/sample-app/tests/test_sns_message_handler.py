from chalice.test import Client
from pytest import fixture
from app import app

LAMDA_NAME = "sns_message_handler"


@fixture(name="test_client")
def fixture_client():
    with Client(app) as client:
        yield client

def test_positive(test_client):
    response = test_client.lambda_.invoke(
        LAMDA_NAME, test_client.events.generate_sns_event(message="hello world")
    )
    assert response.payload == {"message": "hello world"}

def test_negative(test_client):
    response = test_client.lambda_.invoke(
        LAMDA_NAME, test_client.events.generate_sns_event(message="wrong world")
    )
    assert response.payload != {"message": "hello world"}

