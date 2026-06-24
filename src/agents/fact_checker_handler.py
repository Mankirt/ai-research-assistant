from src.agents.fact_checker import FactCheckerAgent, FactCheckInput
from src.agents.handler_factory import create_lambda_handler

lambda_handler = create_lambda_handler(FactCheckerAgent, FactCheckInput)