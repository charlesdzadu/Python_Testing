.PHONY: start install clean test coverage perf help

# Start the Flask application
start:
	@echo "Starting Flask application..."
	@python -m flask --app server run --host=0.0.0.0 --port=5001 --debug

# Install dependencies
install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

# Clean up Python cache files
clean:
	@echo "Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name "*.pyo" -delete

test:
	@echo "Running unit and integration tests..."
	@pytest -q

coverage:
	@echo "Running tests with coverage (target >= 80%)..."
	@pytest --cov=server --cov-report=term-missing --cov-fail-under=80 -q

perf:
	@echo "Starting Locust performance test (default 6 users)..."
	@locust -f tests/perf/locustfile.py --headless -u 6 -r 2 -t 1m --host=http://localhost:5001

# Help command
help:
	@echo "Available commands:"
	@echo "  start   - Start the Flask application"
	@echo "  install - Install dependencies from requirements.txt"
	@echo "  clean   - Clean up Python cache files"
	@echo "  test    - Run unit and integration tests"
	@echo "  coverage- Run tests with coverage and enforce >=80%"
	@echo "  perf    - Run Locust performance tests"
	@echo "  help    - Show this help message"
