from src.agents.critic import CriticAgent, CriticInput
from src.agents.handler_factory import create_lambda_handler

lambda_handler = create_lambda_handler(CriticAgent, CriticInput)