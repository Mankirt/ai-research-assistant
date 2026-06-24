import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.critic import CriticAgent, CriticInput, CriticOutput


@pytest.fixture
def mock_bedrock():
    with patch("src.agents.critic.BedrockClient") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_input():
    return CriticInput(
        topic="artificial intelligence",
        title="The State of AI in 2026",
        report_markdown="# The State of AI\n\nAI is transforming industries..."
    )


@pytest.fixture
def sample_llm_response():
    return json.dumps({
        "topic": "artificial intelligence",
        "score": 8,
        "weaknesses": ["Could use more specific statistics"],
        "suggested_improvements": [
            "Add quantitative data",
            "Include more diverse sources"
        ],
        "verdict": "approved",
        "critique_summary": "Well-structured report with clear claims, minor improvements possible"
    })


def test_critic_runs_successfully(
    mock_bedrock,
    sample_input,
    sample_llm_response
):
    mock_bedrock.invoke.return_value = sample_llm_response

    agent = CriticAgent()
    result = agent.run(sample_input)

    assert isinstance(result, CriticOutput)
    assert result.score == 8
    assert result.verdict == "approved"
    assert len(result.weaknesses) == 1
    assert len(result.suggested_improvements) == 2


def test_critic_strips_markdown_fences(
    mock_bedrock,
    sample_input
):
    fenced_response = """```json
{
    "topic": "artificial intelligence",
    "score": 5,
    "weaknesses": ["Too vague"],
    "suggested_improvements": ["Be more specific"],
    "verdict": "needs_revision",
    "critique_summary": "Needs more depth"
}
```"""
    mock_bedrock.invoke.return_value = fenced_response

    agent = CriticAgent()
    result = agent.run(sample_input)

    assert result.verdict == "needs_revision"
    assert result.score == 5


def test_critic_raises_on_invalid_json(
    mock_bedrock,
    sample_input
):
    mock_bedrock.invoke.return_value = "not valid json"

    agent = CriticAgent()
    with pytest.raises(json.JSONDecodeError):
        agent.run(sample_input)


def test_critic_verdict_matches_low_score(
    mock_bedrock,
    sample_input
):
    low_score_response = json.dumps({
        "topic": "artificial intelligence",
        "score": 3,
        "weaknesses": ["Major issues with sourcing", "Unclear structure"],
        "suggested_improvements": ["Rewrite with better sources"],
        "verdict": "needs_revision",
        "critique_summary": "Significant revision needed"
    })
    mock_bedrock.invoke.return_value = low_score_response

    agent = CriticAgent()
    result = agent.run(sample_input)

    assert result.score == 3
    assert result.verdict == "needs_revision"
