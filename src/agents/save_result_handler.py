import json
from src.utils.dynamodb_client import DynamoDBClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def lambda_handler(event: dict, context) -> dict:
    logger.info(f"Save result invoked with event: {json.dumps(event)}")

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
                "body": json.dumps({"error": "topic is required to save result"})
            }

        db = DynamoDBClient()
        research_id = db.save_research(
            topic=topic,
            status="completed",
            result=body
        )

        logger.info(f"Saved research result with id: {research_id}")

        return {
            "statusCode": 200,
            "body": json.dumps({**body, "research_id": research_id})
        }

    except Exception as e:
        logger.error(f"Failed to save result: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }