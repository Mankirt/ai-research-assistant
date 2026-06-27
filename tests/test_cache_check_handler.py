import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.cache_check_handler import lambda_handler


@pytest.fixture
def mock_db():
    with patch("src.agents.cache_check_handler.DynamoDBClient") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


def test_cache_hit_returns_cached_result(mock_db):
    mock_db.get_cached_research.return_value = {
        "research_id": "abc-123",
        "result": {"topic": "AI", "summary": "cached summary"}
    }

    event = {"body": json.dumps({"topic": "AI"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    assert response["cache_hit"] is True
    body = json.loads(response["body"])
    assert body["summary"] == "cached summary"


def test_cache_miss_returns_topic_only(mock_db):
    mock_db.get_cached_research.return_value = None

    event = {"body": json.dumps({"topic": "quantum computing"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    assert response["cache_hit"] is False
    body = json.loads(response["body"])
    assert body["topic"] == "quantum computing"


def test_missing_topic_returns_422(mock_db):
    event = {"body": json.dumps({})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 422


def test_handles_raw_string_event(mock_db):
    mock_db.get_cached_research.return_value = None

    event = json.dumps({"topic": "AI"})
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    assert response["cache_hit"] is False


def test_handles_db_failure_gracefully(mock_db):
    mock_db.get_cached_research.side_effect = Exception("DynamoDB connection error")

    event = {"body": json.dumps({"topic": "AI"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 500
    assert response["cache_hit"] is False

def test_cache_hit_serializes_decimal_fields(mock_db):
    from decimal import Decimal

    mock_db.get_cached_research.return_value = {
        "research_id": "abc-123",
        "result": {
            "topic": "AI",
            "score": Decimal("8"),
            "summary": "cached summary"
        }
    }

    event = {"body": json.dumps({"topic": "AI"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["score"] == 8