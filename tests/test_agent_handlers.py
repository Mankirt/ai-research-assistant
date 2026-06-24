def test_researcher_handler_imports():
    from src.agents.handler import lambda_handler
    assert callable(lambda_handler)


def test_fact_checker_handler_imports():
    from src.agents.fact_checker_handler import lambda_handler
    assert callable(lambda_handler)


def test_writer_handler_imports():
    from src.agents.writer_handler import lambda_handler
    assert callable(lambda_handler)


def test_critic_handler_imports():
    from src.agents.critic_handler import lambda_handler
    assert callable(lambda_handler)