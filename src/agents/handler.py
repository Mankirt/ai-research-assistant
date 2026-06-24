from src.agents.researcher import ResearcherAgent, ResearchInput
from src.agents.handler_factory import create_lambda_handler

lambda_handler = create_lambda_handler(ResearcherAgent, ResearchInput)