import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.handler import lambda_handler


@pytest.fixture
def mock_researcher():
    with patch("src.agents.handler.ResearcherAgent") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_output():
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {
        "topic": "artificial intelligence",
        "key_facts": ["AI is transforming industries"],
        "conflicting_info": [],
        "credible_sources": ["https://example.com"],
        "summary": "AI is rapidly evolving."
    }
    return mock_output


def test_handler_returns_200_on_success(mock_researcher, sample_output):
    mock_researcher.run.return_value = sample_output

    event = {
        "body": json.dumps({"topic": "artificial intelligence"})
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["topic"] == "artificial intelligence"


def test_handler_returns_400_on_invalid_json(mock_researcher):
    event = {
        "body": "this is not json"
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "Invalid JSON" in body["error"]


def test_handler_returns_422_on_missing_topic(mock_researcher):
    event = {
        "body": json.dumps({"max_results": 5})
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 422
    body = json.loads(response["body"])
    assert "Invalid input" in body["error"]


def test_handler_returns_500_on_agent_failure(mock_researcher):
    mock_researcher.run.side_effect = Exception("Agent crashed")

    event = {
        "body": json.dumps({"topic": "artificial intelligence"})
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert body["error"] == "Internal server error"


def test_handler_accepts_dict_body(mock_researcher, sample_output):
    mock_researcher.run.return_value = sample_output

    event = {
        "body": {"topic": "artificial intelligence"}
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200


def test_handler_never_exposes_internal_errors(mock_researcher):
    mock_researcher.run.side_effect = Exception(
        "Secret internal database connection string"
    )

    event = {
        "body": json.dumps({"topic": "artificial intelligence"})
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert "Secret internal database" not in body["error"]
    assert body["error"] == "Internal server error"