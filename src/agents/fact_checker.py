from pydantic import BaseModel
from src.utils.bedrock_client import BedrockClient
from src.utils.logger import get_logger
from src.prompts.fact_checker_prompt import get_fact_checker_prompt
import json

logger = get_logger(__name__)


class VerifiedFact(BaseModel):
    fact: str
    confidence: str
    reasoning: str


class FactCheckInput(BaseModel):
    topic: str
    key_facts: list[str]
    credible_sources: list[str]
    conflicting_info: list[str] = []


class FactCheckOutput(BaseModel):
    topic: str
    verified_facts: list[VerifiedFact]
    flagged_facts: list[str]
    overall_credibility_score: str
    notes: str


class FactCheckerAgent:
    def __init__(self):
        self.bedrock = BedrockClient()

    def run(self, input_data: FactCheckInput) -> FactCheckOutput:
        logger.info(f"Fact checker agent starting for topic: {input_data.topic}")

        prompt = get_fact_checker_prompt(input_data.model_dump())

        raw_response = self.bedrock.invoke(prompt=prompt, max_tokens=1500)
        logger.info("LLM response received")

        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.split("```")[1]
            if cleaned_response.startswith("json"):
                cleaned_response = cleaned_response[4:]
        cleaned_response = cleaned_response.strip()

        try:
            parsed = json.loads(cleaned_response)
            output = FactCheckOutput(**parsed)
            logger.info("Fact checking completed successfully")
            return output

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Failed to validate fact check output: {str(e)}")
            raise