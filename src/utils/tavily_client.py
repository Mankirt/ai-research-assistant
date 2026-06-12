from tavily import TavilyClient
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TavilySearchClient:
    def __init__(self):
        self.client = TavilyClient(api_key=Config.TAVILY_API_KEY)

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        logger.info(f"Searching Tavily for: {query}")

        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                include_answer=False,
                include_raw_content=False,
            )

            results = response.get("results", [])

            cleaned = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0.0),
                }
                for r in results
            ]

            logger.info(f"Tavily returned {len(cleaned)} results")
            return cleaned

        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            raise