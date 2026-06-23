import json
import pytest
from unittest.mock import MagicMock, patch
from src.agents.writer import WriterAgent, WriterInput, WriterOutput


@pytest.fixture
def mock_bedrock():
    with patch("src.agents.writer.BedrockClient") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_input():
    return WriterInput(
        topic="artificial intelligence",
        verified_facts=[
            {
                "fact": "AI is transforming industries",
                "confidence": "high",
                "reasoning": "Supported by multiple sources"
            }
        ],
        flagged_facts=["Some unverifiable broad claim"],
        overall_credibility_score="medium",
        notes="Most facts well supported"
    )


@pytest.fixture
def sample_llm_response():
    return json.dumps({
        "topic": "artificial intelligence",
        "title": "The State of AI in 2026",
        "report_markdown": "# The State of AI in 2026\n\nAI continues to transform industries...",
        "word_count": 150
    })


def test_writer_runs_successfully(
    mock_bedrock,
    sample_input,
    sample_llm_response
):
    mock_bedrock.invoke.return_value = sample_llm_response

    agent = WriterAgent()
    result = agent.run(sample_input)

    assert isinstance(result, WriterOutput)
    assert result.topic == "artificial intelligence"
    assert "AI" in result.title
    assert result.word_count == 150


def test_writer_strips_markdown_fences(
    mock_bedrock,
    sample_input
):
    fenced_response = """```json
        {
            "topic": "artificial intelligence",
            "title": "Test Report",
            "report_markdown": "# Test\\n\\nContent here",
            "word_count": 50
        }
        ```"""
    mock_bedrock.invoke.return_value = fenced_response

    agent = WriterAgent()
    result = agent.run(sample_input)

    assert result.title == "Test Report"


def test_writer_raises_on_invalid_json(
    mock_bedrock,
    sample_input
):
    mock_bedrock.invoke.return_value = "not valid json"

    agent = WriterAgent()
    with pytest.raises(json.JSONDecodeError):
        agent.run(sample_input)


def test_writer_handles_empty_flagged_facts(
    mock_bedrock,
    sample_llm_response
):
    input_data = WriterInput(
        topic="test topic",
        verified_facts=[{"fact": "test", "confidence": "high", "reasoning": "test"}],
        overall_credibility_score="high"
    )
    mock_bedrock.invoke.return_value = sample_llm_response

    agent = WriterAgent()
    result = agent.run(input_data)

    assert result.topic == "artificial intelligence"  # from mocked response
