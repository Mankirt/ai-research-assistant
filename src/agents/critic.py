from pydantic import BaseModel
from src.utils.bedrock_client import BedrockClient
from src.utils.logger import get_logger
from src.prompts.critic_prompt import get_critic_prompt
import json

logger = get_logger(__name__)


class CriticInput(BaseModel):
    topic: str
    title: str
    report_markdown: str


class CriticOutput(BaseModel):
    topic: str
    score: int
    weaknesses: list[str]
    suggested_improvements: list[str]
    verdict: str
    critique_summary: str


class CriticAgent:
    def __init__(self):
        self.bedrock = BedrockClient()

    def run(self, input_data: CriticInput) -> CriticOutput:
        logger.info(f"Critic agent starting for topic: {input_data.topic}")

        prompt = get_critic_prompt(input_data.model_dump())

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
            output = CriticOutput(**parsed)
            logger.info("Critique completed successfully")
            return output

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Failed to validate critic output: {str(e)}")
            raise