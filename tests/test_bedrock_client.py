import json
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from src.utils.bedrock_client import BedrockClient


@pytest.fixture
def mock_bedrock_client():
    with patch("src.utils.bedrock_client.boto3.client") as mock_boto3:
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        yield mock_client


def test_invoke_returns_text(mock_bedrock_client):
    mock_response_body = {
        "content": [{"text": "This is a test response"}]
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": MagicMock(read=lambda: json.dumps(mock_response_body).encode())
    }

    client = BedrockClient()
    result = client.invoke("Test prompt")

    assert result == "This is a test response"


def test_invoke_calls_correct_model(mock_bedrock_client):
    mock_response_body = {
        "content": [{"text": "response"}]
    }
    mock_bedrock_client.invoke_model.return_value = {
        "body": MagicMock(read=lambda: json.dumps(mock_response_body).encode())
    }

    client = BedrockClient()
    client.invoke("Test prompt")

    call_args = mock_bedrock_client.invoke_model.call_args
    assert "anthropic.claude-haiku-4-5" in call_args.kwargs["modelId"]


def test_invoke_raises_on_client_error(mock_bedrock_client):
    mock_bedrock_client.invoke_model.side_effect = ClientError(
        error_response={
            "Error": {
                "Code": "AccessDeniedException",
                "Message": "Access denied"
            }
        },
        operation_name="InvokeModel"
    )

    client = BedrockClient()
    with pytest.raises(ClientError):
        client.invoke("Test prompt")


def test_invoke_raises_on_unexpected_error(mock_bedrock_client):
    mock_bedrock_client.invoke_model.side_effect = Exception("Unexpected error")

    client = BedrockClient()
    with pytest.raises(Exception):
        client.invoke("Test prompt")