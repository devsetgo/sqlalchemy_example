.PHONY: install run_prod run_dev create_tables help

help:
	@echo "Available targets:"
	@echo "  install       - Install required dependencies"
	@echo "  run_prod      - Run the FastAPI application in production mode"
	@echo "  run_dev       - Run the FastAPI application in development mode with hot-reloading"
	@echo "  create_tables - Create the necessary tables in the database"

install:
	pip install -r requirements.txt

run_prd:
	uvicorn src.main:app --host 0.0.0.0 --port 5000 --workers 1

run_dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
