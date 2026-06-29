import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.pipeline_handler import lambda_handler


@pytest.fixture
def mock_sfn_client():
    with patch("src.agents.pipeline_handler.boto3.client") as mock_boto:
        mock_client = MagicMock()
        mock_boto.return_value = mock_client
        yield mock_client


def test_options_request_short_circuits(mock_sfn_client):
    event = {
        "requestContext": {"http": {"method": "OPTIONS"}},
        "body": None
    }
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_sfn_client.start_execution.assert_not_called()


def test_missing_topic_returns_422(mock_sfn_client):
    event = {"body": json.dumps({})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 422


def test_invalid_json_returns_400(mock_sfn_client):
    event = {"body": "not valid json"}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 400


def test_successful_execution_returns_200(mock_sfn_client):
    mock_sfn_client.start_execution.return_value = {
        "executionArn": "arn:aws:states:us-east-1:123:execution:test:abc"
    }
    mock_sfn_client.describe_execution.return_value = {
        "status": "SUCCEEDED",
        "output": json.dumps({"topic": "AI", "score": 8})
    }

    event = {"body": json.dumps({"topic": "AI"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["topic"] == "AI"
    assert body["score"] == 8


def test_successful_execution_handles_double_encoded_output(mock_sfn_client):
    mock_sfn_client.start_execution.return_value = {
        "executionArn": "arn:aws:states:us-east-1:123:execution:test:abc"
    }
    # Simulates the ReturnCached Pass-state output shape (string within string)
    mock_sfn_client.describe_execution.return_value = {
        "status": "SUCCEEDED",
        "output": json.dumps(json.dumps({"topic": "AI", "score": 9}))
    }

    event = {"body": json.dumps({"topic": "AI"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["score"] == 9


def test_failed_execution_returns_500(mock_sfn_client):
    mock_sfn_client.start_execution.return_value = {
        "executionArn": "arn:aws:states:us-east-1:123:execution:test:abc"
    }
    mock_sfn_client.describe_execution.return_value = {
        "status": "FAILED",
        "error": "States.Runtime"
    }

    event = {"body": json.dumps({"topic": "AI"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 500


def test_start_execution_failure_returns_500(mock_sfn_client):
    mock_sfn_client.start_execution.side_effect = Exception("AWS error")

    event = {"body": json.dumps({"topic": "AI"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 500


def test_timeout_returns_504(mock_sfn_client):
    mock_sfn_client.start_execution.return_value = {
        "executionArn": "arn:aws:states:us-east-1:123:execution:test:abc"
    }
    mock_sfn_client.describe_execution.return_value = {
        "status": "RUNNING"
    }

    with patch("src.agents.pipeline_handler.time.sleep"):  # skip real sleep delays
        event = {"body": json.dumps({"topic": "AI"})}
        response = lambda_handler(event, None)

    assert response["statusCode"] == 504