.PHONY: install test lint clean run

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

lint:
	pip install flake8
	flake8 src/ tests/

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Remove cache files"
	@echo "  make lint     - Run linter"