import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.fact_checker import FactCheckerAgent, FactCheckInput, FactCheckOutput


@pytest.fixture
def mock_bedrock():
    with patch("src.agents.fact_checker.BedrockClient") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_input():
    return FactCheckInput(
        topic="artificial intelligence",
        key_facts=[
            "AI is transforming industries",
            "Models are becoming more efficient"
        ],
        credible_sources=[
            "https://example.com/ai",
            "https://example.com/ml"
        ],
        conflicting_info=[]
    )


@pytest.fixture
def sample_llm_response():
    return json.dumps({
        "topic": "artificial intelligence",
        "verified_facts": [
            {
                "fact": "AI is transforming industries",
                "confidence": "high",
                "reasoning": "Supported by multiple credible sources"
            }
        ],
        "flagged_facts": ["Models are becoming more efficient"],
        "overall_credibility_score": "medium",
        "notes": "Most facts well supported, one claim too broad to verify"
    })


def test_fact_checker_runs_successfully(
    mock_bedrock,
    sample_input,
    sample_llm_response
):
    mock_bedrock.invoke.return_value = sample_llm_response

    agent = FactCheckerAgent()
    result = agent.run(sample_input)

    assert isinstance(result, FactCheckOutput)
    assert result.topic == "artificial intelligence"
    assert len(result.verified_facts) == 1
    assert result.verified_facts[0].confidence == "high"
    assert len(result.flagged_facts) == 1


def test_fact_checker_strips_markdown_fences(
    mock_bedrock,
    sample_input
):
    fenced_response = """```json
{
    "topic": "artificial intelligence",
    "verified_facts": [],
    "flagged_facts": [],
    "overall_credibility_score": "low",
    "notes": "No facts provided"
}
```"""
    mock_bedrock.invoke.return_value = fenced_response

    agent = FactCheckerAgent()
    result = agent.run(sample_input)

    assert result.overall_credibility_score == "low"


def test_fact_checker_raises_on_invalid_json(
    mock_bedrock,
    sample_input
):
    mock_bedrock.invoke.return_value = "not valid json"

    agent = FactCheckerAgent()
    with pytest.raises(json.JSONDecodeError):
        agent.run(sample_input)


def test_fact_checker_handles_empty_conflicting_info(
    mock_bedrock,
    sample_llm_response
):
    input_data = FactCheckInput(
        topic="test topic",
        key_facts=["fact 1"],
        credible_sources=["https://example.com"]
        # conflicting_info defaults to []
    )
    mock_bedrock.invoke.return_value = sample_llm_response

    agent = FactCheckerAgent()
    result = agent.run(input_data)

    assert result.topic == "artificial intelligence"  # from mocked response


