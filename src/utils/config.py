import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCOUNT_ID: str = os.getenv("AWS_ACCOUNT_ID", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID",
        "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    )

    @classmethod
    def validate(cls):
        missing = []
        if not cls.AWS_ACCOUNT_ID:
            missing.append("AWS_ACCOUNT_ID")
        if not cls.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")