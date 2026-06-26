import time
import pytest
from unittest.mock import MagicMock, patch
from src.utils.dynamodb_client import DynamoDBClient


@pytest.fixture
def mock_table():
    with patch("src.utils.dynamodb_client.boto3.resource") as mock_resource:
        mock_table_instance = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table_instance
        yield mock_table_instance


def test_save_research_returns_id(mock_table):
    client = DynamoDBClient()
    research_id = client.save_research(
        topic="quantum computing",
        status="completed",
        result={"summary": "test summary"}
    )

    assert isinstance(research_id, str)
    assert len(research_id) > 0
    mock_table.put_item.assert_called_once()


def test_save_research_stores_lowercase_topic(mock_table):
    client = DynamoDBClient()
    client.save_research(
        topic="Quantum Computing",
        status="completed",
        result={}
    )

    call_args = mock_table.put_item.call_args
    item = call_args.kwargs["Item"]
    assert item["topic_lower"] == "quantum computing"
    assert item["topic"] == "Quantum Computing"


def test_get_cached_research_returns_none_when_empty(mock_table):
    mock_table.scan.return_value = {"Items": []}

    client = DynamoDBClient()
    result = client.get_cached_research("quantum computing")

    assert result is None


def test_get_cached_research_returns_recent_match(mock_table):
    now = int(time.time())
    mock_table.scan.return_value = {
        "Items": [
            {
                "research_id": "abc-123",
                "topic": "quantum computing",
                "topic_lower": "quantum computing",
                "status": "completed",
                "result": {"summary": "test"},
                "created_at": now - 100  # 100 seconds ago, fresh
            }
        ]
    }

    client = DynamoDBClient()
    result = client.get_cached_research("quantum computing")

    assert result is not None
    assert result["research_id"] == "abc-123"


def test_get_cached_research_ignores_stale_results(mock_table):
    now = int(time.time())
    stale_timestamp = now - (25 * 60 * 60)  # 25 hours ago, stale

    mock_table.scan.return_value = {
        "Items": [
            {
                "research_id": "old-456",
                "topic": "quantum computing",
                "topic_lower": "quantum computing",
                "status": "completed",
                "result": {},
                "created_at": stale_timestamp
            }
        ]
    }

    client = DynamoDBClient()
    result = client.get_cached_research("quantum computing")

    assert result is None


def test_get_cached_research_returns_most_recent_when_multiple(mock_table):
    now = int(time.time())
    mock_table.scan.return_value = {
        "Items": [
            {
                "research_id": "older",
                "topic_lower": "ai",
                "status": "completed",
                "result": {},
                "created_at": now - 5000
            },
            {
                "research_id": "newer",
                "topic_lower": "ai",
                "status": "completed",
                "result": {},
                "created_at": now - 100
            }
        ]
    }

    client = DynamoDBClient()
    result = client.get_cached_research("ai")

    assert result["research_id"] == "newer"