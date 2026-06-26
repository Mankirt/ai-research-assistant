import json
from src.utils.dynamodb_client import DynamoDBClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def lambda_handler(event: dict, context) -> dict:
    logger.info(f"Cache check invoked with event: {json.dumps(event)}")

    try:
        if isinstance(event, str):
            body = json.loads(event)
        elif isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", event)

        topic = body.get("topic")
        if not topic:
            return {
                "statusCode": 422,
                "body": json.dumps({"error": "topic is required"})
            }

        db = DynamoDBClient()
        cached = db.get_cached_research(topic)

        if cached:
            logger.info(f"Cache hit for topic: {topic}")
            return {
                "statusCode": 200,
                "cache_hit": True,
                "body": json.dumps(cached["result"])
            }

        logger.info(f"Cache miss for topic: {topic}")
        return {
            "statusCode": 200,
            "cache_hit": False,
            "body": json.dumps({"topic": topic})
        }

    except Exception as e:
        logger.error(f"Cache check failed: {str(e)}")
        return {
            "statusCode": 500,
            "cache_hit": False,
            "body": json.dumps({"error": "Internal server error"})
        }