from src.agents.writer import WriterAgent, WriterInput
from src.agents.handler_factory import create_lambda_handler

lambda_handler = create_lambda_handler(WriterAgent, WriterInput)