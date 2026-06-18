import json
from src.agents.researcher import ResearcherAgent, ResearchInput
from src.utils.logger import get_logger

logger = get_logger(__name__)


def lambda_handler(event: dict, context) -> dict:
    logger.info(f"Lambda invoked with event: {json.dumps(event)}")

    try:
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", event)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }

    try:
        input_data = ResearchInput(**body)

    except Exception as e:
        logger.error(f"Invalid input: {str(e)}")
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Invalid input: {str(e)}"})
        }

    try:
        agent = ResearcherAgent()
        result = agent.run(input_data)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result.model_dump())
        }

    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"})
        }