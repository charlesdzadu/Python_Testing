.PHONY: start install clean

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

# Help command
help:
	@echo "Available commands:"
	@echo "  start   - Start the Flask application"
	@echo "  install - Install dependencies from requirements.txt"
	@echo "  clean   - Clean up Python cache files"
	@echo "  help    - Show this help message"
