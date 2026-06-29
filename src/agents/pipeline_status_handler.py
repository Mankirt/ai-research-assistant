import json
import boto3
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Maps Step Functions state names to frontend-friendly step keys
STATE_NAME_MAP = {
    "CacheCheck": "cache_check",
    "Research": "research",
    "FactCheck": "factcheck",
    "Write": "write",
    "Critique": "critique",
    "SaveResult": "save_result",
}


def lambda_handler(event: dict, context) -> dict:
    logger.info(f"Pipeline status invoked with event: {json.dumps(event)}")

    request_context = event.get("requestContext", {}) if isinstance(event, dict) else {}
    http_method = request_context.get("http", {}).get("method", "")
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({})
        }

    query_params = event.get("queryStringParameters") or {}
    execution_arn = query_params.get("execution_arn")

    if not execution_arn:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "execution_arn is required"})
        }

    try:
        sf_client = boto3.client("stepfunctions", region_name=Config.AWS_REGION)
        execution = sf_client.describe_execution(executionArn=execution_arn)
        status = execution["status"]

        if status == "SUCCEEDED":
            output = json.loads(execution["output"])
            if isinstance(output, str):
                output = json.loads(output)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "SUCCEEDED",
                    "current_step": None,
                    "result": output
                })
            }

        if status == "FAILED":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "FAILED",
                    "current_step": None,
                    "result": None
                })
            }

        # Still RUNNING — find the current active step
        history = sf_client.get_execution_history(
            executionArn=execution_arn,
            maxResults=20,
            reverseOrder=True
        )

        current_step = None
        for evt in history["events"]:
            if evt["type"] == "TaskStateEntered":
                state_name = evt["stateEnteredEventDetails"]["name"]
                current_step = STATE_NAME_MAP.get(state_name, state_name)
                break

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "RUNNING",
                "current_step": current_step,
                "result": None
            })
        }

    except Exception as e:
        logger.error(f"Failed to check execution status: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Failed to check pipeline status"})
        }