import json
import boto3
from src.utils.config import Config
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger(__name__)

STATE_MACHINE_ARN = "arn:aws:states:us-east-1:513616570472:stateMachine:research-pipeline"


def lambda_handler(event: dict, context) -> dict:
    logger.info(f"Start pipeline invoked with event: {json.dumps(event)}")

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
    
    if len(topic) > 200:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Topic must be under 200 characters"})
        }

    try:
        sf_client = boto3.client("stepfunctions", region_name=Config.AWS_REGION)
        execution = sf_client.start_execution(
            stateMachineArn=Config.STATE_MACHINE_ARN,
            input=json.dumps({"body": json.dumps({"topic": topic})})
        )
        execution_arn = execution["executionArn"]
        logger.info(f"Started execution: {execution_arn}")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"execution_arn": execution_arn})
        }

    except Exception as e:
        logger.error(f"Failed to start execution: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Failed to start research pipeline"})
        }