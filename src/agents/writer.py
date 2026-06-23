from pydantic import BaseModel
from src.utils.bedrock_client import BedrockClient
from src.utils.logger import get_logger
from src.prompts.writer_prompt import get_writer_prompt
import json

logger = get_logger(__name__)


class WriterInput(BaseModel):
    topic: str
    verified_facts: list[dict]
    flagged_facts: list[str] = []
    overall_credibility_score: str
    notes: str = ""


class WriterOutput(BaseModel):
    topic: str
    title: str
    report_markdown: str
    word_count: int


class WriterAgent:
    def __init__(self):
        self.bedrock = BedrockClient()

    def run(self, input_data: WriterInput) -> WriterOutput:
        logger.info(f"Writer agent starting for topic: {input_data.topic}")

        prompt = get_writer_prompt(input_data.model_dump())


        raw_response = self.bedrock.invoke(prompt=prompt, max_tokens=2000)
        logger.info("LLM response received")

        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.split("```")[1]
            if cleaned_response.startswith("json"):
                cleaned_response = cleaned_response[4:]
        cleaned_response = cleaned_response.strip()

        try:
            parsed = json.loads(cleaned_response)
            output = WriterOutput(**parsed)
            logger.info("Report writing completed successfully")
            return output

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Failed to validate writer output: {str(e)}")
            raise