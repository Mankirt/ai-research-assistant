import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.save_result_handler import lambda_handler


@pytest.fixture
def mock_db():
    with patch("src.agents.save_result_handler.DynamoDBClient") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


def test_save_result_returns_research_id(mock_db):
    mock_db.save_research.return_value = "abc-123-id"

    event = {
        "body": json.dumps({
            "topic": "quantum computing",
            "score": 8,
            "verdict": "approved"
        })
    }
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["research_id"] == "abc-123-id"
    assert body["topic"] == "quantum computing"
    assert body["score"] == 8


def test_save_result_calls_db_with_correct_topic(mock_db):
    mock_db.save_research.return_value = "xyz-456"

    event = {
        "body": json.dumps({
            "topic": "artificial intelligence",
            "score": 7
        })
    }
    lambda_handler(event, None)

    call_args = mock_db.save_research.call_args
    assert call_args.kwargs["topic"] == "artificial intelligence"
    assert call_args.kwargs["status"] == "completed"


def test_missing_topic_returns_422(mock_db):
    event = {"body": json.dumps({"score": 5})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 422


def test_handles_raw_string_event(mock_db):
    mock_db.save_research.return_value = "test-id"

    event = json.dumps({"topic": "AI", "score": 9})
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["research_id"] == "test-id"


def test_handles_db_failure_gracefully(mock_db):
    mock_db.save_research.side_effect = Exception("DynamoDB write error")

    event = {"body": json.dumps({"topic": "AI", "score": 5})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 500