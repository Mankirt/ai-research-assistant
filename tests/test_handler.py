import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.handler_factory import create_lambda_handler
from pydantic import BaseModel


class DummyInput(BaseModel):
    topic: str


class DummyOutput(BaseModel):
    topic: str
    result: str


class DummyAgent:
    def run(self, input_data: DummyInput) -> DummyOutput:
        return DummyOutput(topic=input_data.topic, result="processed")


@pytest.fixture
def handler():
    return create_lambda_handler(DummyAgent, DummyInput)


def test_handler_returns_200_on_success(handler):
    event = {"body": json.dumps({"topic": "test topic"})}
    response = handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["topic"] == "test topic"
    assert body["result"] == "processed"


def test_handler_returns_400_on_invalid_json(handler):
    event = {"body": "this is not json"}
    response = handler(event, None)

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "Invalid JSON" in body["error"]


def test_handler_returns_422_on_missing_required_field(handler):
    event = {"body": json.dumps({})}
    response = handler(event, None)

    assert response["statusCode"] == 422
    body = json.loads(response["body"])
    assert "Invalid input" in body["error"]


def test_handler_returns_500_on_agent_failure():
    class FailingAgent:
        def run(self, input_data):
            raise Exception("Agent crashed")

    failing_handler = create_lambda_handler(FailingAgent, DummyInput)
    event = {"body": json.dumps({"topic": "test"})}
    response = failing_handler(event, None)

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert body["error"] == "Internal server error"


def test_handler_accepts_dict_body(handler):
    event = {"body": {"topic": "test topic"}}
    response = handler(event, None)

    assert response["statusCode"] == 200


def test_handler_never_exposes_internal_errors():
    class FailingAgent:
        def run(self, input_data):
            raise Exception("Secret internal database connection string")

    failing_handler = create_lambda_handler(FailingAgent, DummyInput)
    event = {"body": json.dumps({"topic": "test"})}
    response = failing_handler(event, None)

    body = json.loads(response["body"])
    assert "Secret internal database" not in body["error"]
    assert body["error"] == "Internal server error"

def test_handler_accepts_raw_string_event(handler):
    # Step Functions passes the previous state's output body directly as a string
    event = json.dumps({"topic": "test topic"})
    response = handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["topic"] == "test topic"