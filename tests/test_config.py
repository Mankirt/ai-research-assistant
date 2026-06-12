import pytest
from unittest.mock import patch
from src.utils.config import Config


def test_default_region():
    assert Config.AWS_REGION == "us-east-1"


def test_default_model_id():
    assert Config.BEDROCK_MODEL_ID == "anthropic.claude-3-haiku-20240307-v1:0"


def test_validate_raises_when_missing_keys():
    with patch.object(Config, "AWS_ACCOUNT_ID", ""):
        with patch.object(Config, "TAVILY_API_KEY", ""):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert "AWS_ACCOUNT_ID" in str(exc_info.value)
            assert "TAVILY_API_KEY" in str(exc_info.value)


def test_validate_passes_when_keys_present():
    with patch.object(Config, "AWS_ACCOUNT_ID", "123456789012"):
        with patch.object(Config, "TAVILY_API_KEY", "test-key"):
            Config.validate()  # should not raise