.PHONY: setup run-api run-sequential run-batch test lint format clean

# Setup and installation
setup:
	pip install -r requirements.txt

# Run commands
run-api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-sequential:
	python -m app.run --mode sequential

run-batch:
	python -m app.run --mode batch

# Testing
test:
	pytest -xvs

# Code quality
lint:
	flake8 app tests
	isort --check-only --profile black app tests
	black --check app tests

format:
	isort --profile black app tests
	black app tests

# Database commands
db-init:
	python -m app.db.init

db-reset:
	python -m app.db.init --reset

# Clean up
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

# Help command
help:
	@echo "Available commands:"
	@echo "  setup          - Install dependencies"
	@echo "  run-api        - Run the API server with hot reload"
	@echo "  run-sequential - Run the application in sequential mode"
	@echo "  run-batch      - Run the application in batch mode"
	@echo "  test           - Run tests"
	@echo "  lint           - Check code quality"
	@echo "  format         - Format code"
	@echo "  db-init        - Initialize database"
	@echo "  db-reset       - Reset database (caution: deletes all data)"
	@echo "  clean          - Clean temporary files" 