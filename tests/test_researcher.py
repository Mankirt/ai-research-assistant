import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.researcher import ResearcherAgent, ResearchInput, ResearchOutput


@pytest.fixture
def mock_tavily():
    with patch("src.agents.researcher.TavilySearchClient") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_bedrock():
    with patch("src.agents.researcher.BedrockClient") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_search_results():
    return [
        {
            "title": "AI in 2025",
            "url": "https://example.com/ai",
            "content": "AI is transforming industries rapidly.",
            "score": 0.95
        },
        {
            "title": "Machine Learning Trends",
            "url": "https://example.com/ml",
            "content": "Machine learning models are getting more efficient.",
            "score": 0.89
        }
    ]


@pytest.fixture
def sample_llm_response():
    return json.dumps({
        "topic": "artificial intelligence",
        "key_facts": [
            "AI is transforming industries",
            "Models are becoming more efficient"
        ],
        "conflicting_info": [],
        "credible_sources": [
            "https://example.com/ai",
            "https://example.com/ml"
        ],
        "summary": "AI is rapidly evolving and transforming industries."
    })


def test_researcher_runs_successfully(
    mock_tavily,
    mock_bedrock,
    sample_search_results,
    sample_llm_response
):
    mock_tavily.search.return_value = sample_search_results
    mock_bedrock.invoke.return_value = sample_llm_response

    agent = ResearcherAgent()
    result = agent.run(ResearchInput(topic="artificial intelligence"))

    assert isinstance(result, ResearchOutput)
    assert result.topic == "artificial intelligence"
    assert len(result.key_facts) == 2
    assert len(result.credible_sources) == 2


def test_researcher_calls_tavily_with_correct_topic(
    mock_tavily,
    mock_bedrock,
    sample_search_results,
    sample_llm_response
):
    mock_tavily.search.return_value = sample_search_results
    mock_bedrock.invoke.return_value = sample_llm_response

    agent = ResearcherAgent()
    agent.run(ResearchInput(topic="quantum computing"))

    mock_tavily.search.assert_called_once_with(
        query="quantum computing",
        max_results=5
    )


def test_researcher_raises_on_invalid_json(
    mock_tavily,
    mock_bedrock,
    sample_search_results
):
    mock_tavily.search.return_value = sample_search_results
    mock_bedrock.invoke.return_value = "this is not valid json"

    agent = ResearcherAgent()
    with pytest.raises(json.JSONDecodeError):
        agent.run(ResearchInput(topic="artificial intelligence"))


def test_researcher_respects_max_results(
    mock_tavily,
    mock_bedrock,
    sample_search_results,
    sample_llm_response
):
    mock_tavily.search.return_value = sample_search_results
    mock_bedrock.invoke.return_value = sample_llm_response

    agent = ResearcherAgent()
    agent.run(ResearchInput(topic="AI", max_results=3))

    mock_tavily.search.assert_called_once_with(
        query="AI",
        max_results=3
    )