from pydantic import BaseModel
from src.utils.bedrock_client import BedrockClient
from src.utils.tavily_client import TavilySearchClient
from src.utils.logger import get_logger
from src.prompts.researcher_prompt import get_researcher_prompt
import json

logger = get_logger(__name__)


class ResearchInput(BaseModel):
    topic: str
    max_results: int = 5


class ResearchOutput(BaseModel):
    topic: str
    key_facts: list[str]
    conflicting_info: list[str]
    credible_sources: list[str]
    summary: str


class ResearcherAgent:
    def __init__(self):
        self.bedrock = BedrockClient()
        self.tavily = TavilySearchClient()

    def run(self, input_data: ResearchInput) -> ResearchOutput:
        logger.info(f"Researcher agent starting for topic: {input_data.topic}")

        search_results = self.tavily.search(
            query=input_data.topic,
            max_results=input_data.max_results
        )
        logger.info(f"Retrieved {len(search_results)} search results")

        prompt = get_researcher_prompt(
            topic=input_data.topic,
            search_results=search_results
        )

        raw_response = self.bedrock.invoke(prompt=prompt, max_tokens=1000)
        logger.info("LLM response received")
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.split("```")[1]
            if cleaned_response.startswith("json"):
                cleaned_response = cleaned_response[4:]
        cleaned_response = cleaned_response.strip()
        try:
            parsed = json.loads(cleaned_response)
            output = ResearchOutput(**parsed)
            logger.info("Research completed successfully")
            return output

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Failed to validate research output: {str(e)}")
            raise