import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.pipeline_status_handler import lambda_handler


@pytest.fixture
def mock_sfn_client():
    with patch("src.agents.pipeline_status_handler.boto3.client") as mock_boto:
        mock_client = MagicMock()
        mock_boto.return_value = mock_client
        yield mock_client


def test_options_request_short_circuits(mock_sfn_client):
    event = {
        "requestContext": {"http": {"method": "OPTIONS"}},
        "queryStringParameters": None
    }
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    mock_sfn_client.describe_execution.assert_not_called()


def test_missing_execution_arn_returns_422(mock_sfn_client):
    event = {"queryStringParameters": {}}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 422


def test_succeeded_execution_returns_result(mock_sfn_client):
    mock_sfn_client.describe_execution.return_value = {
        "status": "SUCCEEDED",
        "output": json.dumps({"topic": "AI", "score": 8})
    }

    event = {"queryStringParameters": {"execution_arn": "arn:test:123"}}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "SUCCEEDED"
    assert body["result"]["score"] == 8
    assert body["current_step"] is None


def test_succeeded_execution_handles_double_encoded_output(mock_sfn_client):
    mock_sfn_client.describe_execution.return_value = {
        "status": "SUCCEEDED",
        "output": json.dumps(json.dumps({"topic": "AI", "score": 9}))
    }

    event = {"queryStringParameters": {"execution_arn": "arn:test:123"}}
    response = lambda_handler(event, None)

    body = json.loads(response["body"])
    assert body["result"]["score"] == 9


def test_failed_execution_returns_failed_status(mock_sfn_client):
    mock_sfn_client.describe_execution.return_value = {"status": "FAILED"}

    event = {"queryStringParameters": {"execution_arn": "arn:test:123"}}
    response = lambda_handler(event, None)

    body = json.loads(response["body"])
    assert body["status"] == "FAILED"
    assert body["result"] is None


def test_running_execution_returns_current_step(mock_sfn_client):
    mock_sfn_client.describe_execution.return_value = {"status": "RUNNING"}
    mock_sfn_client.get_execution_history.return_value = {
        "events": [
            {
                "type": "TaskStateEntered",
                "stateEnteredEventDetails": {"name": "FactCheck"}
            }
        ]
    }

    event = {"queryStringParameters": {"execution_arn": "arn:test:123"}}
    response = lambda_handler(event, None)

    body = json.loads(response["body"])
    assert body["status"] == "RUNNING"
    assert body["current_step"] == "factcheck"


def test_running_execution_with_no_task_state_yet(mock_sfn_client):
    mock_sfn_client.describe_execution.return_value = {"status": "RUNNING"}
    mock_sfn_client.get_execution_history.return_value = {"events": []}

    event = {"queryStringParameters": {"execution_arn": "arn:test:123"}}
    response = lambda_handler(event, None)

    body = json.loads(response["body"])
    assert body["current_step"] is None


def test_describe_execution_failure_returns_500(mock_sfn_client):
    mock_sfn_client.describe_execution.side_effect = Exception("AWS error")

    event = {"queryStringParameters": {"execution_arn": "arn:test:123"}}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 500