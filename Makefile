.PHONY: help test run install clean lint

help:
	@echo "Available targets:"
	@echo "  make test     - Run all unit tests"
	@echo "  make run      - Run the development server"
	@echo "  make install  - Install dependencies"
	@echo "  make clean    - Clean up Python cache files"
	@echo "  make lint     - Run code linting"

test:
	pytest test_app.py -v --tb=short

test-coverage:
	pytest test_app.py -v --cov=. --cov-report=html

run:
	python main.py

install:
	pip install -r requirements.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .coverage htmlcov

lint:
	pylint *.py --disable=C0111,C0103

.DEFAULT_GOAL := help
