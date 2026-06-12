import pytest
from unittest.mock import MagicMock, patch
from src.utils.tavily_client import TavilySearchClient


@pytest.fixture
def mock_tavily():
    with patch("src.utils.tavily_client.TavilyClient") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


def test_search_returns_cleaned_results(mock_tavily):
    mock_tavily.search.return_value = {
        "results": [
            {
                "title": "Test Title",
                "url": "https://example.com",
                "content": "Test content here",
                "score": 0.95,
                "extra_field": "should be removed"
            }
        ]
    }

    client = TavilySearchClient()
    results = client.search("test query")

    assert len(results) == 1
    assert results[0]["title"] == "Test Title"
    assert results[0]["url"] == "https://example.com"
    assert results[0]["content"] == "Test content here"
    assert results[0]["score"] == 0.95
    assert "extra_field" not in results[0]


def test_search_returns_empty_list_when_no_results(mock_tavily):
    mock_tavily.search.return_value = {"results": []}

    client = TavilySearchClient()
    results = client.search("test query")

    assert results == []


def test_search_respects_max_results(mock_tavily):
    mock_tavily.search.return_value = {"results": []}

    client = TavilySearchClient()
    client.search("test query", max_results=3)

    call_args = mock_tavily.search.call_args
    assert call_args.kwargs["max_results"] == 3


def test_search_raises_on_failure(mock_tavily):
    mock_tavily.search.side_effect = Exception("API failure")

    client = TavilySearchClient()
    with pytest.raises(Exception) as exc_info:
        client.search("test query")

    assert "API failure" in str(exc_info.value)