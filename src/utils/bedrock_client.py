import json
import boto3
from botocore.exceptions import ClientError
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BedrockClient:
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=Config.AWS_REGION
        )
        self.model_id = Config.BEDROCK_MODEL_ID

    def invoke(self, prompt: str, max_tokens: int = 1000) -> str:
        logger.info(f"Invoking Bedrock model: {self.model_id}")

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            response_body = json.loads(response["body"].read())
            content = response_body["content"][0]["text"]

            logger.info("Bedrock invocation successful")
            return content

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Bedrock ClientError: {error_code} - {error_message}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error invoking Bedrock: {str(e)}")
            raise