import boto3
import time
import uuid
from boto3.dynamodb.conditions import Attr
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours


class DynamoDBClient:
    def __init__(self, table_name: str = "research_runs"):
        self.client = boto3.resource("dynamodb", region_name=Config.AWS_REGION)
        self.table = self.client.Table(table_name)

    def save_research(self, topic: str, status: str, result: dict) -> str:
        research_id = str(uuid.uuid4())
        now = int(time.time())

        item = {
            "research_id": research_id,
            "topic": topic,
            "topic_lower": topic.lower(),
            "status": status,
            "result": result,
            "created_at": now,
        }

        try:
            self.table.put_item(Item=item)
            logger.info(f"Saved research run {research_id} for topic: {topic}")
            return research_id

        except Exception as e:
            logger.error(f"Failed to save research run: {str(e)}")
            raise

    def get_cached_research(self, topic: str) -> dict | None:
        try:
            response = self.table.scan(
                FilterExpression=Attr("topic_lower").eq(topic.lower())
                & Attr("status").eq("completed")
            )

            items = response.get("Items", [])

            if not items:
                logger.info(f"No cached research found for topic: {topic}")
                return None

            # Sort by most recent, check if still within TTL
            items.sort(key=lambda x: x["created_at"], reverse=True)
            most_recent = items[0]

            age_seconds = int(time.time()) - most_recent["created_at"]
            if age_seconds > CACHE_TTL_SECONDS:
                logger.info(f"Cached research for '{topic}' is stale ({age_seconds}s old)")
                return None

            logger.info(f"Found cached research for topic: {topic}")
            return most_recent

        except Exception as e:
            logger.error(f"Failed to check cache for topic: {str(e)}")
            raise