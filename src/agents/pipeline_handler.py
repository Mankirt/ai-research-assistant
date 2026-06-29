import json
import time
import boto3
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

STATE_MACHINE_ARN = "arn:aws:states:us-east-1:513616570472:stateMachine:research-pipeline"
POLL_INTERVAL_SECONDS = 2
MAX_POLL_ATTEMPTS = 25  # ~50 seconds max wait


def lambda_handler(event: dict, context) -> dict:
    logger.info(f"Pipeline handler invoked with event: {json.dumps(event)}")

    request_context = event.get("requestContext", {}) if isinstance(event, dict) else {}
    http_method = request_context.get("http", {}).get("method", "")
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({})
        }

    try:
        if isinstance(event, str):
            body = json.loads(event)
        elif isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", event)

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }

    topic = body.get("topic")
    if not topic:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "topic is required"})
        }

    try:
        sf_client = boto3.client("stepfunctions", region_name=Config.AWS_REGION)
        execution = sf_client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({"body": json.dumps({"topic": topic})})
        )
        execution_arn = execution["executionArn"]
        logger.info(f"Started execution: {execution_arn}")

    except Exception as e:
        logger.error(f"Failed to start execution: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Failed to start research pipeline"})
        }

    for attempt in range(MAX_POLL_ATTEMPTS):
        time.sleep(POLL_INTERVAL_SECONDS)

        try:
            status_response = sf_client.describe_execution(executionArn=execution_arn)
            status = status_response["status"]

            if status == "SUCCEEDED":
                output = json.loads(status_response["output"])
                # Output may itself be a JSON string (from ReturnCached Pass state)
                if isinstance(output, str):
                    output = json.loads(output)
                logger.info(f"Execution succeeded after {attempt + 1} polls")
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(output)
                }

            if status == "FAILED":
                logger.error(f"Execution failed: {status_response.get('error', 'unknown')}")
                return {
                    "statusCode": 500,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Research pipeline failed"})
                }

        except Exception as e:
            logger.error(f"Error polling execution: {str(e)}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error"})
            }

    logger.error("Execution timed out after max poll attempts")
    return {
        "statusCode": 504,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "Research pipeline timed out"})
    }